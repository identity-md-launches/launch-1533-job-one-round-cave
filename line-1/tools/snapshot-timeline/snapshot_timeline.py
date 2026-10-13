#!/usr/bin/env python3
"""Build a bounded offline timeline of validated ZTO supply snapshots."""
import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'timeline_snapshot_seal', TOOLS / 'snapshot-seal' / 'snapshot_seal.py')
seal = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(seal)
MAX_INPUTS = 16
SCHEMA = 'pinned-zto-timeline/1'


def observation(raw, index):
    """Validate one exact input, retaining a digest of the bytes inspected."""
    if len(raw) > seal.MAX_BYTES:
        raise ValueError('snapshot exceeds 4 MiB')
    bundle = seal.pinned.rpc.strict_json(raw)
    facts = seal.pinned.inspect(bundle)
    block = bundle['block']
    return {
        'input_index': index,
        'sha256': hashlib.sha256(raw).hexdigest(),
        'captured_at': bundle['captured_at'],
        'endpoint': bundle['endpoint'],
        'requested_block': bundle['requested_block'],
        'block_number': facts['block_number'],
        'block_hash': facts['block_hash'].lower(),
        'parent_hash': block['parentHash'].lower(),
        'block_timestamp': str(int(block['timestamp'], 16)),
        'token': facts['token'],
        'total_supply_base_units': facts['total_supply_base_units'],
    }


def timeline(raw_inputs):
    """Return evidence and conflicts, without inferring unsampled history."""
    if not 1 <= len(raw_inputs) <= MAX_INPUTS:
        raise ValueError('provide between 1 and 16 snapshots')
    rows = [observation(raw, index) for index, raw in enumerate(raw_inputs)]
    rows.sort(key=lambda row: (int(row['block_number']), row['block_hash'],
                               row['captured_at'], row['sha256'], row['input_index']))
    by_number = defaultdict(list)
    for row in rows:
        by_number[int(row['block_number'])].append(row)
    groups = []
    conflicts = []
    for number in sorted(by_number):
        by_hash = defaultdict(list)
        for row in by_number[number]:
            by_hash[row['block_hash']].append(row)
        variants = []
        issues = []
        if len(by_hash) > 1:
            issues.append('different_hashes_at_same_height')
        for block_hash, members in sorted(by_hash.items()):
            headers = {(r['parent_hash'], r['block_timestamp']) for r in members}
            supplies = sorted({r['total_supply_base_units'] for r in members}, key=int)
            if len(headers) > 1:
                issues.append('different_headers_for_same_hash')
            if len(supplies) > 1:
                issues.append('different_supplies_for_same_hash')
            variants.append({
                'block_hash': block_hash,
                'headers': [{'parent_hash': parent, 'timestamp': stamp}
                            for parent, stamp in sorted(headers)],
                'total_supply_base_units': supplies,
                'input_indexes': sorted(r['input_index'] for r in members),
            })
        issues = sorted(set(issues))
        if issues:
            conflicts.append({'block_number': str(number), 'issues': issues})
        groups.append({'block_number': str(number), 'variants': variants,
                       'issues': issues})

    transitions = []
    for left, right in zip(groups, groups[1:]):
        left_n, right_n = int(left['block_number']), int(right['block_number'])
        row = {'from_block': str(left_n), 'to_block': str(right_n),
               'blocks_between': str(right_n - left_n - 1),
               'total_supply_delta_base_units': None,
               'parent_link': 'not_checked_gap'}
        if not left['issues'] and not right['issues']:
            a, b = left['variants'][0], right['variants'][0]
            row['total_supply_delta_base_units'] = str(
                int(b['total_supply_base_units'][0]) -
                int(a['total_supply_base_units'][0]))
            if right_n == left_n + 1:
                row['parent_link'] = ('matches' if b['headers'][0]['parent_hash'] ==
                                      a['block_hash'] else 'conflict')
                if row['parent_link'] == 'conflict':
                    conflicts.append({'from_block': str(left_n), 'to_block': str(right_n),
                                      'issues': ['parent_hash_does_not_link']})
        else:
            row['parent_link'] = 'not_checked_conflict'
        transitions.append(row)
    return {
        'schema': SCHEMA,
        'token': seal.pinned.ZTO,
        'input_count': len(rows),
        'observations': rows,
        'blocks': groups,
        'transitions': transitions,
        'conflicts': conflicts,
        'status': 'conflict' if conflicts else 'consistent_observations',
        'network_used': False,
        'evidence_limits': ('Provider responses are validated structurally and bound to '
                            'input bytes. No provider authentication, independent agreement, '
                            'block-hash recomputation, finality, complete history, or cause '
                            'of a supply change is established. Gaps are unsampled.'),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    report = sub.add_parser('report', help='inspect one to sixteen workspace snapshot files')
    report.add_argument('snapshots', nargs='+')
    sub.add_parser('demo', help='inspect retained real ZTO observations offline')
    args = parser.parse_args(argv)
    try:
        paths = ([TOOLS / 'pinned-snapshot' / 'example-zto.json',
                  TOOLS / 'snapshot-seal' / 'current-zto.json'] if
                 args.command == 'demo' else args.snapshots)
        if not 1 <= len(paths) <= MAX_INPUTS:
            raise ValueError('wrong number of snapshots')
        result = timeline([seal.read_bytes(path) for path in paths])
    except (OSError, ValueError, TypeError, KeyError, RuntimeError, UnicodeError,
            RecursionError, OverflowError):
        print('snapshot-timeline: invalid, missing, or inconsistent snapshot',
              file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2 if result['status'] == 'conflict' else 0


if __name__ == '__main__':
    raise SystemExit(main())
