#!/usr/bin/env python3
"""Behavior tests use memory and test/scratch; no network or payload execution."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
from unittest import mock
import unittest
import zipfile

spec = importlib.util.spec_from_file_location('dependency_tests',
    'line-2/tools/handoff-dependencies/dependencies.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Dependencies(unittest.TestCase):
    def setUp(self):
        self.files = {'app.py': b'public app', 'lib.py': b'public library',
                      'data/é': b'', 'unrelated': b'unselected bytes'}
        self.data = m.WRITER.build(self.files)
        self.graph = {'app.py': ['lib.py'], 'lib.py': ['data/é'], 'data/é': []}

    def test_transitive_closure_exact_bytes_and_omission(self):
        output, receipt = m.select_bytes(self.data, ['app.py'], self.graph)
        self.assertEqual(receipt['added_dependency_paths'], ['data/é', 'lib.py'])
        self.assertEqual(receipt['subset']['omitted_paths'], ['unrelated'])
        with zipfile.ZipFile(io.BytesIO(output)) as archive:
            self.assertEqual(set(archive.namelist()), set(self.graph) | {'HANDOFF.json'})
            for path in self.graph:
                self.assertEqual(archive.read(path), self.files[path])
        self.assertTrue(m.INSPECT.inspect_stream(io.BytesIO(output))['verified'])

    def test_multiple_roots_shared_dependency(self):
        graph = dict(self.graph, unrelated=['lib.py'])
        output, receipt = m.select_bytes(self.data, ['unrelated', 'app.py'], graph)
        self.assertEqual(output, self.data)
        self.assertEqual(receipt['roots'], ['app.py', 'unrelated'])
        self.assertEqual(receipt['graph_edge_count'], 3)

    def test_cycles_and_self_edge_terminate(self):
        graph = {'app.py': ['lib.py'], 'lib.py': ['app.py', 'lib.py']}
        _, receipt = m.select_bytes(self.data, ['app.py'], graph)
        self.assertEqual(receipt['added_dependency_paths'], ['lib.py'])

    def test_deep_graph_no_recursion(self):
        files = {str(i): b'' for i in range(900)}
        graph = {str(i): [str(i + 1)] if i < 899 else [] for i in range(900)}
        output, receipt = m.select_bytes(m.WRITER.build(files), ['0'], graph)
        self.assertEqual(receipt['subset']['file_count'], 900)
        self.assertEqual(output, m.WRITER.build(files))

    def test_order_independent_graph_roots_and_edges(self):
        graph = dict(self.graph, unrelated=['app.py', 'lib.py'])
        a = m.select_bytes(self.data, ['unrelated', 'data/é'], graph)
        reversed_graph = {p: list(reversed(v)) for p, v in reversed(list(graph.items()))}
        b = m.select_bytes(self.data, ['data/é', 'unrelated'], reversed_graph)
        self.assertEqual(a, b)

    def test_unselected_declaration_recorded_and_validated(self):
        graph = dict(self.graph, unrelated=[])
        _, receipt = m.select_bytes(self.data, ['app.py'], graph)
        self.assertEqual(receipt['unselected_declared_paths'], ['unrelated'])
        with self.assertRaisesRegex(ValueError, 'absent'):
            m.select_bytes(self.data, ['app.py'], dict(self.graph, missing=[]))

    def test_undeclared_roots_and_dependencies(self):
        for roots, graph in ((['unrelated'], self.graph),
                             (['app.py'], {'app.py': ['lib.py']})):
            with self.subTest(graph=graph), self.assertRaisesRegex(ValueError, 'undeclared'):
                m.select_bytes(self.data, roots, graph)

    def test_bad_roots(self):
        for roots in ([], ['app.py', 'app.py'], 'app.py', [None], ['HANDOFF.json'],
                      ['../escape'], ['/absolute'], ['dir/'], ['a\\b']):
            with self.subTest(roots=roots), self.assertRaises(ValueError):
                m.select_bytes(self.data, roots, self.graph)

    def test_bad_graphs(self):
        for graph in ({}, [], {'app.py': 'lib.py'}, {'app.py': ['lib.py', 'lib.py']},
                      {'app.py': [None]}, {'HANDOFF.json': []}, {'../x': []},
                      {'app.py': [] , 'x' * 1025: []}):
            with self.subTest(graph=graph), self.assertRaises(ValueError):
                m.select_bytes(self.data, ['app.py'], graph)

    def test_declaration_conflicts(self):
        for edges, leaves in (([], ['lib.py', 'lib.py']),
                              ([['lib.py', 'app.py']], ['lib.py'])):
            with self.assertRaises(ValueError):
                m.declarations(edges, leaves)
        graph = m.declarations([['app.py', 'lib.py'], ['app.py', 'lib.py']], ['lib.py'])
        with self.assertRaisesRegex(ValueError, 'duplicate dependency'):
            m.select_bytes(self.data, ['app.py'], graph)

    def test_graph_and_archive_budgets(self):
        for limits in (m.INSPECT.Limits(files=1), m.INSPECT.Limits(archive_bytes=1),
                       m.INSPECT.Limits(payload_bytes=1)):
            with self.assertRaises(ValueError):
                m.select_bytes(self.data, ['app.py'], self.graph, limits=limits)
        with mock.patch.object(m, 'MAX_EDGES', 1), self.assertRaisesRegex(ValueError, 'edge limit'):
            m.select_bytes(self.data, ['app.py'], self.graph)
        with mock.patch.object(m, 'MAX_GRAPH_BYTES', 1), self.assertRaisesRegex(ValueError, 'byte limit'):
            m.select_bytes(self.data, ['app.py'], self.graph)

    def test_source_digest_pin(self):
        _, receipt = m.select_bytes(self.data, ['app.py'], self.graph,
                                    m.WRITER.digest(self.data).upper())
        self.assertTrue(receipt['subset']['source_trusted_digest_matched'])
        for bad in ('no', 'f' * 64):
            with self.assertRaises(ValueError):
                m.select_bytes(self.data, ['app.py'], self.graph, bad)

    def test_corrupt_omitted_file_refused(self):
        changed = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(self.data)) as source, zipfile.ZipFile(changed, 'w') as target:
            for entry in source.infolist():
                content = source.read(entry.filename)
                target.writestr(entry, b'X' * len(content) if entry.filename == 'unrelated' else content)
        with self.assertRaisesRegex(ValueError, 'integrity mismatch'):
            m.select_bytes(changed.getvalue(), ['app.py'], self.graph)

    def test_mutable_snapshot_frozen(self):
        data = bytearray(self.data)
        original = m.SUBSET.select_bytes
        def mutate(snapshot, *args):
            data[:] = b'changed'
            return original(snapshot, *args)
        with mock.patch.object(m.SUBSET, 'select_bytes', mutate):
            _, receipt = m.select_bytes(data, ['app.py'], self.graph)
        self.assertEqual(receipt['subset']['source_archive_sha256'], m.WRITER.digest(self.data))

    def test_path_single_read_and_early_declaration_refusal(self):
        graph = {'README.md': ['handoff.py'], 'handoff.py': []}
        with mock.patch.object(m.WRITER, 'regular_bytes', wraps=m.WRITER.regular_bytes) as reader:
            m.select_path('line-2/handoff.zip', ['README.md'], graph)
            self.assertEqual(reader.call_count, 1)
        with mock.patch.object(m.WRITER, 'regular_bytes', side_effect=AssertionError('read')):
            with self.assertRaisesRegex(ValueError, 'undeclared'):
                m.select_path('line-2/handoff.zip', ['README.md'], {'README.md': ['handoff.py']})

    def test_workspace_confinement(self):
        for path in ('../outside', '/tmp/outside'):
            with self.assertRaises(ValueError):
                m.select_path(path, ['app.py'], self.graph)
        root = Path('test/scratch/handoff-dependencies')
        root.mkdir(parents=True, exist_ok=True)
        link = root / 'symlink.zip'
        if link.is_symlink(): link.unlink()
        link.symlink_to('missing.zip')
        try:
            with self.assertRaises(ValueError):
                m.select_path(str(link), ['app.py'], self.graph)
            with self.assertRaises(ValueError):
                m.SUBSET.save_new(str(link), b'ignored')
        finally:
            link.unlink()

    def run_cli(self, args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = m.main(args)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_cli_preview_and_exclusive_output(self):
        root = Path('test/scratch/handoff-dependencies')
        root.mkdir(parents=True, exist_ok=True)
        output = root / 'selected.zip'
        if output.exists(): output.unlink()
        args = ['select', 'line-2/handoff.zip', '--file', 'README.md',
                '--requires', 'README.md', 'handoff.py', '--leaf', 'handoff.py']
        code, stdout, stderr = self.run_cli(args)
        self.assertEqual(code, 0)
        self.assertEqual(stderr, '')
        self.assertEqual(json.loads(stdout)['subset']['file_count'], 2)
        code, stdout, _ = self.run_cli(args + ['--output', str(output)])
        self.assertEqual(code, 0)
        before = output.read_bytes()
        self.assertEqual(m.WRITER.digest(before), json.loads(stdout)['subset']['subset_archive_sha256'])
        code, stdout, stderr = self.run_cli(args + ['--output', str(output)])
        self.assertEqual(code, 1)
        self.assertEqual(stdout, '')
        self.assertTrue(stderr)
        self.assertEqual(output.read_bytes(), before)
        self.assertFalse((root / 'handoff.py').exists())
        output.unlink()

    def test_cli_failure_has_no_receipt_or_output(self):
        output = Path('test/scratch/handoff-dependencies/refused.zip')
        if output.exists(): output.unlink()
        code, stdout, stderr = self.run_cli(['select', 'line-2/handoff.zip', '--file',
            'README.md', '--requires', 'README.md', 'handoff.py', '--output', str(output)])
        self.assertEqual(code, 1)
        self.assertEqual(stdout, '')
        self.assertIn('undeclared', stderr)
        self.assertFalse(output.exists())

    def test_real_archive_demo_no_write(self):
        result = m.demo()
        self.assertTrue(result['reproduced'])
        self.assertEqual(result['added_dependency_paths'], ['handoff.py'])
        self.assertEqual(result['subset']['source_archive_sha256'],
                         result['subset']['subset_archive_sha256'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
