"""Exercise the three remaining companions' actual CLI file boundaries offline."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = HERE.parent / 'transfer-crosscheck/publicnode.json'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ledger = load('bounded_ledger_test', HERE.parent / 'transfer-window-ledger/ledger.py')


class CompanionBoundaryTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / 'test/scratch'
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.path = self.folder / 'capture.json'
        self.path.write_bytes(SOURCE.read_bytes())

    def commands(self, path):
        yield 'ledger', HERE.parent / 'transfer-window-ledger/ledger.py', ['--capture', str(path)]
        yield 'counterparties', HERE.parent / 'transfer-counterparties/counterparties.py', ['--capture', str(path)]
        script = HERE.parent / 'transfer-window-stitch/stitch.py'
        yield 'stitch-left', script, ['--left', str(path), '--right', str(SOURCE)]
        yield 'stitch-right', script, ['--left', str(SOURCE), '--right', str(path)]

    def refuse(self, path, message):
        for name, script, args in self.commands(path):
            with self.subTest(consumer=name):
                result = subprocess.run([sys.executable, '-B', str(script), *args],
                                        cwd=ROOT, capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(result.stdout, '')
                self.assertIn(message, result.stderr)
                self.assertNotIn('Traceback', result.stderr)

    def test_real_zto_capture_through_every_cli(self):
        for name, script, args in self.commands(self.path):
            with self.subTest(consumer=name):
                result = subprocess.run([sys.executable, '-B', str(script), *args],
                                        cwd=ROOT, capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report['token'], 'ZTO')
                count = report.get('transfer_count', report.get('source_transfer_count'))
                self.assertEqual(count, 3)
                self.assertTrue(report['read_only'])

    def test_final_symlink_refused_even_inside_workspace(self):
        link = self.folder / 'link.json'
        link.symlink_to(self.path)
        self.refuse(link, 'cannot read workspace capture')

    def test_directory_symlink_refused(self):
        link = self.folder / 'linked-directory'
        link.symlink_to(self.folder, target_is_directory=True)
        self.refuse(link / 'capture.json', 'cannot read workspace capture')

    def test_traversal_refused_without_resolving_to_valid_file(self):
        child = self.folder / 'child'
        child.mkdir()
        self.refuse(child / '..' / 'capture.json', 'traversal')

    def test_outside_workspace_refused(self):
        self.refuse(ROOT.parent / 'never-open-this.json', 'inside this workspace')

    def test_fifo_refused_without_waiting_for_writer(self):
        fifo = self.folder / 'fifo'
        os.mkfifo(fifo)
        self.refuse(fifo, 'regular file')

    def test_directory_refused(self):
        self.refuse(self.folder, 'regular file')

    def test_duplicate_json_keys_refused(self):
        self.path.write_bytes(b'{"raw_logs":[],"raw_logs":[]}')
        self.refuse(self.path, 'duplicate key')

    def test_nonfinite_and_overflow_json_refused(self):
        for raw in (b'NaN', b'Infinity', b'-Infinity', b'1e999'):
            with self.subTest(raw=raw):
                self.path.write_bytes(raw)
                self.refuse(self.path, 'non-finite')

    def test_excessive_nesting_refused(self):
        self.path.write_bytes(b'[' * 65 + b'0' + b']' * 65)
        self.refuse(self.path, 'nesting')

    def test_invalid_utf8_refused(self):
        self.path.write_bytes(b'\xff')
        self.refuse(self.path, 'strict UTF-8 JSON')

    def test_oversized_file_refused_before_decode(self):
        # Sparse synthetic file: no huge output or dependency is retained.
        with self.path.open('wb') as stream:
            stream.truncate(ledger.MAX_BYTES + 1)
        self.refuse(self.path, 'byte limit')


if __name__ == '__main__':
    unittest.main()
