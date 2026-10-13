"""Behavior checks for recomputation, closure, exact bytes and portable use."""
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
import timeline_handoff as kit

SOURCES = [(kit.HERE / 'examples' / n).read_bytes() for n in ('earlier.json', 'later.json')]


def payloads(data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        return {p: archive.read(p) for p in archive.namelist() if p != 'HANDOFF.json'}


class Tests(unittest.TestCase):
    def test_real_evidence_exact_offline_and_reproducible(self):
        with patch.object(socket, 'socket', side_effect=AssertionError('network')):
            data = kit.build(SOURCES)
            self.assertEqual(data, kit.build(SOURCES))
            receipt = kit.inspect_bytes(data)
        self.assertEqual([payloads(data)[p] for p in kit.names(2)], SOURCES)
        self.assertEqual(receipt['timeline']['status'], 'consistent_observations')
        self.assertEqual(receipt['timeline']['transitions'][0]['total_supply_delta_base_units'], '0')
        self.assertFalse(receipt['network_used'])
        self.assertFalse(receipt['trusted_digest_matched'])
        self.assertEqual(set(receipt['dependency_closure']['added_dependency_paths']),
                         {kit.GRAPH, *kit.names(2)})

    def test_rehashed_false_report_refused(self):
        files = payloads(kit.build(SOURCES))
        obj = json.loads(files[kit.REPORT]); obj['status'] = 'a false claim'
        files[kit.REPORT] = kit.canonical(obj)
        lie = kit.writer.build(files)
        self.assertTrue(kit.inspector.inspect_stream(io.BytesIO(lie))['verified'])
        with self.assertRaisesRegex(ValueError, 'recomputed'):
            kit.inspect_bytes(lie)

    def test_missing_or_added_dependency_refused(self):
        files = payloads(kit.build(SOURCES))
        for p in files:
            fewer = dict(files); del fewer[p]
            with self.subTest(p=p), self.assertRaises(ValueError):
                kit.inspect_bytes(kit.writer.build(fewer))
        with self.assertRaises(ValueError):
            kit.inspect_bytes(kit.writer.build(dict(files, extra=b'x')))

    def test_graph_cannot_omit_source_even_with_valid_manifest(self):
        files = payloads(kit.build(SOURCES))
        graph = json.loads(files[kit.GRAPH]); graph[kit.REPORT].remove('evidence/00.json')
        files[kit.GRAPH] = kit.canonical(graph)
        with self.assertRaisesRegex(ValueError, 'declarations'):
            kit.inspect_bytes(kit.writer.build(files))

    def test_independently_supplied_digest(self):
        data = kit.build(SOURCES)
        self.assertTrue(kit.inspect_bytes(data, hashlib.sha256(data).hexdigest())['trusted_digest_matched'])
        for digest in ('bad', '0' * 64):
            with self.assertRaises(ValueError): kit.inspect_bytes(data, digest)

    def test_conflicts_are_preserved_as_diagnostics(self):
        obj = json.loads(SOURCES[0]); obj['result'] = '0x' + format(1, '064x')
        receipt = kit.inspect_bytes(kit.build([SOURCES[0], kit.canonical(obj)]))
        self.assertEqual(receipt['timeline']['status'], 'conflict')
        self.assertIn('different_supplies_for_same_hash', receipt['timeline']['conflicts'][0]['issues'])

    def test_invalid_snapshot_and_signed_fields_refused(self):
        for change in ({'chain_id': '0x2'}, {'signature': 'not accepted'}, {'result': '0x1'}):
            obj = json.loads(SOURCES[0]); obj.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                kit.build([kit.canonical(obj)])
        for raw in (b'NaN', b'{"x":1,"x":2}', b'\xff', b'1e999'):
            with self.assertRaises((ValueError, TypeError)): kit.build([raw])

    def test_bounds_and_types(self):
        for sources in ([], [SOURCES[0]] * 17, ['text'], [b'x' * (kit.MAX_BYTES + 1)],
                        [SOURCES[1]] * 2):
            with self.assertRaises(ValueError): kit.build(sources)
        with self.assertRaises(ValueError): kit.inspect_bytes(b'x' * (kit.MAX_BYTES + 1))
        with self.assertRaises(ValueError): kit.inspect_bytes(bytearray(b'x'))

    def test_noncanonical_report_bytes_refused(self):
        files = payloads(kit.build(SOURCES))
        files[kit.REPORT] += b' '
        with self.assertRaisesRegex(ValueError, 'recomputed'):
            kit.inspect_bytes(kit.writer.build(files))

    def test_provenance_bytes(self):
        for entry in json.loads((kit.HERE / 'PROVENANCE.json').read_text()):
            copied = (kit.HERE / entry['copy']).read_bytes()
            self.assertEqual(hashlib.sha256(copied).hexdigest(), entry['copy_sha256'])

    def test_workspace_file_boundaries(self):
        scratch = Path('test/scratch'); scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as tmp:
            folder = Path(tmp).relative_to(Path.cwd()); source = folder / 'source.json'; source.write_bytes(SOURCES[0])
            self.assertEqual(kit.read_workspace(str(source)), SOURCES[0])
            link = folder / 'link.json'; link.symlink_to('source.json')
            directory_link = folder / 'dir'; directory_link.symlink_to(folder.resolve(), target_is_directory=True)
            fifo = folder / 'fifo'; os.mkfifo(fifo)
            for p in (link, directory_link / 'source.json', fifo, folder,
                      folder / '..' / 'missing', Path('/never-read-this')):
                with self.subTest(path=p), self.assertRaises((ValueError, OSError)):
                    kit.read_workspace(str(p))

    def test_standalone_cli_exclusive_output_conflict_and_no_extraction(self):
        scratch = Path('test/scratch').resolve(); scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch) as tmp:
            stage = Path(tmp)
            shutil.copytree(kit.HERE, stage / 'kit', ignore=shutil.ignore_patterns('__pycache__'))
            def run(*args):
                return subprocess.run([sys.executable, '-B', 'kit/timeline_handoff.py', *args],
                                      cwd=stage, capture_output=True, text=True, timeout=20)
            self.assertEqual(run('demo').returncode, 0)
            args = ('pack', 'new.zip', 'kit/examples/earlier.json', 'kit/examples/later.json')
            first = run(*args); self.assertEqual(first.returncode, 0, first.stderr)
            before = (stage / 'new.zip').read_bytes()
            self.assertEqual(run('check', 'new.zip').returncode, 0)
            self.assertEqual(run(*args).returncode, 1)
            self.assertEqual((stage / 'new.zip').read_bytes(), before)
            self.assertFalse((stage / 'evidence').exists())
            obj = json.loads(SOURCES[0]); obj['result'] = '0x' + format(1, '064x')
            (stage / 'conflict.json').write_bytes(kit.canonical(obj))
            result = run('pack', 'conflict.zip', 'kit/examples/earlier.json', 'conflict.json')
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(run('check', 'conflict.zip').returncode, 2)
            (stage / 'invalid.json').write_bytes(b'not JSON')
            result = run('pack', 'invalid.zip', 'invalid.json')
            self.assertEqual(result.returncode, 1); self.assertEqual(result.stdout, '')
            self.assertFalse((stage / 'invalid.zip').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
