"""Offline behavior checks for the multi-snapshot ZTO timeline."""
import copy
import hashlib
import io
import json
from pathlib import Path
import socket
import unittest
from unittest.mock import patch

import snapshot_timeline as tool


SOURCE = tool.TOOLS / 'pinned-snapshot' / 'example-zto.json'


def encode(value):
    return json.dumps(value, sort_keys=True).encode()


class TimelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = SOURCE.read_bytes()
        cls.bundle = tool.seal.pinned.rpc.strict_json(cls.raw)

    def test_real_observations_offline(self):
        other = tool.TOOLS / 'snapshot-seal' / 'current-zto.json'
        with patch.object(socket, 'socket', side_effect=AssertionError('network opened')):
            output = tool.timeline([other.read_bytes(), self.raw])
        self.assertEqual(output['status'], 'consistent_observations')
        self.assertEqual([int(x['block_number']) for x in output['blocks']],
                         [26177368, 26180977])
        self.assertEqual(output['transitions'][0]['blocks_between'], '3608')
        self.assertEqual(output['transitions'][0]['total_supply_delta_base_units'], '0')
        self.assertEqual(output['transitions'][0]['parent_link'], 'not_checked_gap')
        self.assertEqual(output['observations'][0]['input_index'], 1)
        self.assertEqual(output['observations'][0]['sha256'], hashlib.sha256(self.raw).hexdigest())

    def test_supply_conflict_at_same_hash(self):
        changed = copy.deepcopy(self.bundle)
        changed['result'] = '0x' + (int(changed['result'], 16) + 1).to_bytes(32, 'big').hex()
        output = tool.timeline([self.raw, encode(changed)])
        self.assertEqual(output['blocks'][0]['issues'], ['different_supplies_for_same_hash'])
        self.assertEqual(output['status'], 'conflict')

    def test_different_hash_at_same_height(self):
        changed = copy.deepcopy(self.bundle)
        new_hash = '0x' + 'ab' * 32
        changed['block']['hash'] = new_hash
        changed['block_after']['hash'] = new_hash
        output = tool.timeline([self.raw, encode(changed)])
        self.assertIn('different_hashes_at_same_height', output['blocks'][0]['issues'])

    def test_same_hash_different_header(self):
        changed = copy.deepcopy(self.bundle)
        changed['block']['parentHash'] = '0x' + 'ab' * 32
        changed['block_after']['parentHash'] = '0x' + 'ab' * 32
        output = tool.timeline([self.raw, encode(changed)])
        self.assertIn('different_headers_for_same_hash', output['blocks'][0]['issues'])

    def test_consecutive_parent_link_conflict(self):
        changed = copy.deepcopy(self.bundle)
        number = int(changed['block']['number'], 16) + 1
        for key in ('block', 'block_after'):
            changed[key]['number'] = hex(number)
            changed[key]['hash'] = '0x' + 'cd' * 32
        changed['params'][1] = hex(number)
        output = tool.timeline([self.raw, encode(changed)])
        self.assertEqual(output['transitions'][0]['parent_link'], 'conflict')
        self.assertEqual(output['status'], 'conflict')

    def test_duplicate_keys_rejected(self):
        self.assertRaises(ValueError, tool.timeline, [b'{"schema":1,"schema":2}'])

    def test_modified_result_without_matching_after_rejected(self):
        changed = copy.deepcopy(self.bundle)
        changed['block_after']['hash'] = '0x' + 'ab' * 32
        self.assertRaises(ValueError, tool.timeline, [encode(changed)])

    def test_limits(self):
        self.assertRaises(ValueError, tool.timeline, [])
        self.assertRaises(ValueError, tool.timeline, [self.raw] * 17)
        self.assertRaises(ValueError, tool.timeline, [b' ' * (tool.seal.MAX_BYTES + 1)])

    def test_demo_command(self):
        output = io.StringIO()
        with patch('sys.stdout', output), patch.object(socket, 'socket',
                                                         side_effect=AssertionError('network opened')):
            code = tool.main(['demo'])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output.getvalue())['input_count'], 2)


if __name__ == '__main__':
    unittest.main()
