#!/usr/bin/env python3
"""Carry a ZTO timeline with its exact observations, recomputing at receipt."""
import argparse
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import struct
import sys
import zipfile

HERE = Path(__file__).resolve().parent
MAX_BYTES = 99_000
REPORT = 'review/timeline.json'
GRAPH = 'review/dependencies.json'


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, HERE / 'vendor' / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


timeline = load('handoff_timeline', 'snapshot-timeline/snapshot_timeline.py')
dependencies = load('handoff_dependencies', 'handoff-dependencies/dependencies.py')
writer = dependencies.WRITER
inspector = dependencies.INSPECT
LIMITS = inspector.Limits(archive_bytes=MAX_BYTES, payload_bytes=MAX_BYTES,
                         manifest_bytes=8192, metadata_bytes=8192, files=18)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def names(count):
    if type(count) is not int or not 1 <= count <= timeline.MAX_INPUTS:
        raise ValueError('provide one to sixteen observations')
    return [f'evidence/{i:02d}.json' for i in range(count)]


def graph_for(count):
    paths = names(count)
    return {REPORT: [GRAPH, *paths], GRAPH: [], **{p: [] for p in paths}}


def recompute(sources):
    if any(not isinstance(raw, bytes) or len(raw) > MAX_BYTES for raw in sources):
        raise ValueError('observations must be bounded original bytes')
    names(len(sources))
    return timeline.timeline(sources)


def inspect_bytes(data, expected=None):
    """Verify all payloads, fixed dependency closure, and exact recomputed report."""
    if not isinstance(data, bytes) or len(data) > MAX_BYTES:
        raise ValueError('archive must be bounded bytes')
    receipt = inspector.inspect_stream(io.BytesIO(data), LIMITS, expected)
    count = receipt['file_count'] - 2
    paths = names(count)
    graph = graph_for(count)
    if {f['path'] for f in receipt['files']} != set(graph):
        raise ValueError('exact numbered observations, graph and report required')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        files = {name: archive.read(name) for name in graph}
    if files[GRAPH] != canonical(graph):
        raise ValueError('dependency declarations differ from the fixed evidence contract')
    report = recompute([files[p] for p in paths])
    if files[REPORT] != canonical(report):
        raise ValueError('timeline differs from the recomputed observations')
    selected, closure = dependencies.select_bytes(data, [REPORT], graph, expected, LIMITS)
    if selected != data:
        raise ValueError('archive is not byte-reproducible under the original writer')
    return {'schema': 'zto-timeline-handoff/1', 'verified': True,
            'timeline_recomputed': True, 'byte_reproducible': True,
            'network_used': False, 'archive_sha256': receipt['archive_sha256'],
            'archive_bytes': len(data), 'trusted_digest_matched': expected is not None,
            'source_sha256': {p: hashlib.sha256(files[p]).hexdigest() for p in paths},
            'dependency_closure': closure, 'timeline': report,
            'limitations': 'Byte integrity and provider-observation consistency only. '
            'Not authenticated providers, finality, complete history, balances or supply-change causes. '
            'The graph retains evidence needed to recompute, not executable tool dependencies. '
            'Nothing is extracted or executed from an archive.'}


def build(sources):
    report = recompute(sources)
    graph = graph_for(len(sources))
    files = {p: raw for p, raw in zip(names(len(sources)), sources)}
    files.update({GRAPH: canonical(graph), REPORT: canonical(report)})
    if sum(map(len, files.values())) > MAX_BYTES:
        raise ValueError('combined payload exceeds 99000 bytes')
    full = writer.build(files)
    selected, _ = dependencies.select_bytes(full, [REPORT], graph, limits=LIMITS)
    inspect_bytes(selected)
    return selected


def read_workspace(raw):
    """Bounded descriptor-relative regular-file read from the chosen workspace."""
    path = Path(raw)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ValueError('relative workspace path without traversal required')
    if not all(hasattr(os, n) for n in ('O_DIRECTORY', 'O_NOFOLLOW', 'O_NONBLOCK')):
        raise ValueError('no-follow file reads require POSIX flags')
    directory = os.open(Path.cwd(), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in path.parts[:-1]:
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                            dir_fd=directory)
            os.close(directory)
            directory = child
        descriptor = os.open(path.parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                             dir_fd=directory)
        with os.fdopen(descriptor, 'rb') as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_BYTES:
                raise ValueError('bounded regular file required')
            result = stream.read(MAX_BYTES + 1)
        if len(result) > MAX_BYTES:
            raise ValueError('file grew past byte limit')
        return result
    finally:
        os.close(directory)


def demo():
    # Trusted bundled dated public observations; never live RPC calls.
    sources = [(HERE / 'examples' / name).read_bytes() for name in ('earlier.json', 'later.json')]
    data = build(sources)
    if data != build(sources):
        raise ValueError('packaging did not reproduce')
    return inspect_bytes(data)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('demo')
    pack = commands.add_parser('pack')
    pack.add_argument('archive', help='new workspace-relative ZIP')
    pack.add_argument('snapshots', nargs='+')
    check = commands.add_parser('check')
    check.add_argument('archive')
    check.add_argument('--sha256', help='independently obtained archive digest')
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            result = demo()
        elif args.command == 'pack':
            names(len(args.snapshots))
            data = build([read_workspace(p) for p in args.snapshots])
            result = inspect_bytes(data)
            dependencies.SUBSET.save_new(args.archive, data)
            result['output'] = args.archive
        else:
            result = inspect_bytes(read_workspace(args.archive), args.sha256)
        print(json.dumps(result, indent=2, sort_keys=True))
        # Conflicts remain useful review evidence, never a readiness claim.
        return 2 if result['timeline']['status'] == 'conflict' else 0
    except (OSError, ValueError, TypeError, KeyError, RuntimeError, UnicodeError,
            RecursionError, OverflowError, zipfile.BadZipFile, EOFError,
            NotImplementedError, struct.error):
        print('timeline-handoff: invalid, inconsistent or over-limit input; no receipt', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
