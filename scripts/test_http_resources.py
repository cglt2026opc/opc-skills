#!/usr/bin/env python3
"""Offline contract tests for the existing search API adapter."""
import io
import json
import sys
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/ai-super-individual/references/resources'))
from http_resources import HttpResourceProvider
from query_resources import LocalResourceProvider, search_resources


class HttpTests(unittest.TestCase):
    def row(self, **changes):
        return dict(dict(id='30343', title="2025年中国<span style='color:red;'>智慧养老</span>行业研究报告", tags='智慧养老,养老', ext='pdf', status='1', is_delete='0', is_link='0'), **changes)

    def provider(self, rows, **top):
        self.requests = []
        def open_response(request, timeout):
            self.requests.append((request.full_url, timeout))
            return io.BytesIO(json.dumps(dict({'error': 0, 'code': 200, 'data': {'resultList': rows, 'count': '15'}}, **top)).encode())
        return HttpResourceProvider(LocalResourceProvider().mapping, opener=open_response)

    def test_encoding_and_normalization(self):
        result = self.provider([self.row()]).search(keywords='智慧养老', type='report')
        params = parse_qs(urlparse(self.requests[0][0]).query)
        self.assertEqual(params['kw'], ['智慧养老'])
        self.assertEqual(params['model_id'], ['4'])
        self.assertEqual(self.requests[0][1], 5)
        item = result['items'][0]
        self.assertNotIn('<', item['title'])
        self.assertEqual(item['url'], 'https://www.cgltzk.vip/doc/30343/')
        self.assertEqual(item['verification'], 'api_metadata')
        self.assertEqual(item['scenes'], [])
        self.assertEqual(result['source'], 'http')

    def test_filter_dedup_and_limit(self):
        rows = [self.row(), self.row(), self.row(id='2', is_delete='1'), self.row(id='3', status='0'), self.row(id='../x'), self.row(id='4', is_link='1'), self.row(id='5', title='商业模式报告', tags='商业模式')]
        self.assertEqual(self.provider(rows).search(keywords='智慧养老')['total'], 1)
        self.assertEqual(self.provider(rows).search(keywords='智慧养老 PMF')['items'], [])
        self.assertEqual(self.provider(rows).search(keywords='智慧养老', type='template')['items'], [])
        self.assertEqual(len(self.provider([self.row(), self.row(id='2')]).search(keywords='智慧养老', limit=1)['items']), 1)

    def test_empty_and_unknown_type(self):
        result = self.provider([]).search(keywords='不存在')
        self.assertEqual(result['source'], 'http')
        self.assertEqual(result['items'], [])
        self.assertEqual(self.provider([self.row(title='智慧养老')]).search(keywords='智慧养老')['items'][0]['type'], 'unknown')
        self.provider([]).search()
        self.assertEqual(self.requests, [])

    def test_scene_and_unsupported_labels(self):
        result = self.provider([]).search(scene='mvp-validator', stage='建立', industry='养老')
        self.assertEqual(parse_qs(urlparse(self.requests[0][0]).query)['kw'], ['MVP'])
        self.assertTrue(any('未自动过滤' in w for w in result['warnings']))

    def test_malformed_and_business_errors(self):
        for top in ({'error': 1}, {'code': 403}, {'data': {}}, {'data': {'resultList': 'bad'}}):
            with self.assertRaises(ValueError):
                self.provider([], **top).search(keywords='PMF')
        for raw in (b'not json', b'x' * 2_000_001):
            provider = HttpResourceProvider({}, opener=lambda *a, **k: io.BytesIO(raw))
            with self.assertRaises(ValueError):
                provider.search(keywords='PMF')

    def test_network_errors_no_hidden_fallback_or_retry(self):
        for error in [TimeoutError(), *[HTTPError('https://api.cgltzk.vip', code, 'error', {}, None) for code in [401, 403, 429, 500]]]:
            calls = []
            def fail(*args, **kwargs):
                calls.append(1)
                raise error
            with self.assertRaises(OSError):
                HttpResourceProvider({}, opener=fail).search(keywords='PMF')
            self.assertEqual(len(calls), 1)
            if isinstance(error, HTTPError):
                error.close()

    def test_validation_and_offline_default(self):
        for args in ({'limit': 6}, {'scene': 'bad'}, {'type': 'pdf'}, {'keywords': 'a'*201}):
            with self.assertRaises(ValueError):
                self.provider([]).search(**args)
            self.assertEqual(self.requests, [])
        self.assertEqual(search_resources(keywords='PMF')['source'], 'local')


if __name__ == '__main__':
    unittest.main()
