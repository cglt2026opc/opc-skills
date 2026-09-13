#!/usr/bin/env python3
"""Resource filtering and relocated-distribution regression tests, fully offline."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from opc_skills import AGENT_TARGETS, REPO_ROOT, selected_skills, discover_modules

RESOURCE_ROOT = REPO_ROOT / 'skills/ai-super-individual/references/resources'
spec = importlib.util.spec_from_file_location('query_resources', RESOURCE_ROOT / 'query_resources.py')
query = importlib.util.module_from_spec(spec)
spec.loader.exec_module(query)


class ResourceTests(unittest.TestCase):
    def setUp(self):
        self.provider = query.LocalResourceProvider()

    def test_index_integrity(self):
        self.assertEqual(set(self.provider.mapping), set(discover_modules()))
        ids = set()
        for item in self.provider.items:
            self.assertNotIn(item['id'], ids)
            ids.add(item['id'])
            for field in ('title', 'url', 'purpose', 'suitable_for', 'access', 'verified_at'):
                self.assertTrue(item[field])
            self.assertIn(item['type'], query.TYPES)
            self.assertLessEqual(set(item['scenes']), set(discover_modules()))

    def test_mvp_and_formats(self):
        result = self.provider.search(scene='mvp-validator', keywords='pmf', type='worksheet')
        self.assertEqual([x['id'] for x in result['items']], ['cgltzk-31523'])
        self.assertEqual(result['items'][0]['format'], 'docx')
        self.assertEqual(self.provider.search(scene='opc-positioner', type='template')['items'][0]['format'], 'xlsx')
        self.assertEqual(self.provider.search(scene='content-planner')['items'][0]['format'], 'pptx')

    def test_no_unrelated_fallback(self):
        for args in ({}, {'scene': 'content-planner', 'keywords': '量子农业白皮书'},
                     {'keywords': 'PMF', 'type': 'case'}, {'scene': 'mvp-validator', 'stage': '突破'},
                     {'keywords': 'Agent 工单', 'industry': '医疗'}):
            self.assertEqual(self.provider.search(**args)['items'], [], args)

    def test_limit_dedup_and_invalid_records(self):
        valid = self.provider.items[0]
        self.provider.items.extend([dict(valid), {**valid, 'id': 'mock', 'is_mock': True},
                                    {**valid, 'id': 'gone', 'status': 'inactive'},
                                    {**valid, 'id': 'bad', 'url': 'https://example.org/a'}])
        result = self.provider.search(scene='opc-modeler')
        self.assertEqual(len({x['url'] for x in result['items']}), len(result['items']))
        self.assertFalse({'mock', 'gone', 'bad'} & {x['id'] for x in result['items']})
        self.assertEqual(len(self.provider.search(scene='opc-modeler', limit=1)['items']), 1)

    def test_invalid_input(self):
        for args in ({'limit': 0}, {'limit': 6}, {'limit': True}, {'scene': 'missing'}, {'type': 'xlsx'}):
            with self.assertRaises(ValueError):
                self.provider.search(**args)
        result = subprocess.run([sys.executable, str(RESOURCE_ROOT / 'query_resources.py'), '--limit', '0'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('error', json.loads(result.stderr))

    def test_damaged_index(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(OSError):
                query.LocalResourceProvider(directory)
            Path(directory, 'resource-map.json').write_text('{}')
            Path(directory, 'cgltzk-resources.json').write_text('{invalid')
            with self.assertRaises(ValueError):
                query.LocalResourceProvider(directory)

    def test_relocated_standalone_query(self):
        with selected_skills(['mvp-validator', 'knowledge-explorer']) as exported:
            for root in exported.values():
                script = root / 'references/opc-shared/resources/query_resources.py'
                result = subprocess.run([sys.executable, str(script), '--keywords', 'PMF'], cwd=tempfile.gettempdir(), capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)['items'][0]['id'], 'cgltzk-31523')

    def test_agent_installs_and_paste_export(self):
        with tempfile.TemporaryDirectory() as directory:
            for agent in AGENT_TARGETS:
                target = Path(directory) / agent
                subprocess.run([sys.executable, str(REPO_ROOT / 'scripts/opc_skills.py'), 'install', '--agent', agent, '--target', str(target)], check=True, capture_output=True)
                self.assertTrue((target / 'ai-super-individual/references/resources/cgltzk-resources.json').exists())
            subprocess.run([sys.executable, str(REPO_ROOT / 'scripts/opc_skills.py'), 'package', '--agent', 'doubao', '--skill', 'mvp-validator', '--output', directory], check=True, capture_output=True)
            text = Path(directory, 'doubao/mvp-validator.prompt.md').read_text()
            self.assertIn('cgltzk-31523', text)
            self.assertIn((RESOURCE_ROOT / 'ACCESS.md').read_text().strip(), text)


if __name__ == '__main__':
    unittest.main()
