#!/usr/bin/env python3
"""Resource query with offline default and optional public HTTP search."""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TYPES = ('template', 'report', 'case', 'tutorial', 'plan', 'worksheet', 'collection')


class LocalResourceProvider:
    def __init__(self, directory=ROOT):
        directory = Path(directory)
        self.mapping = json.loads((directory / 'resource-map.json').read_text(encoding='utf-8'))
        data = json.loads((directory / 'cgltzk-resources.json').read_text(encoding='utf-8'))
        if data.get('schema_version') != '1.0' or not isinstance(data.get('resources'), list):
            raise ValueError('不支持的资源数据结构')
        self.items = data['resources']
        self.updated_at = data['updated_at']

    def search(self, *, keywords='', scene='', stage='', type='', limit=5, industry=''):
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 5:
            raise ValueError('limit 必须为 1～5')
        if type and type not in TYPES:
            raise ValueError('不支持的资源类型')
        if scene and scene not in self.mapping:
            raise ValueError('未知 scene；请使用模块名或留空')
        terms = {x.casefold() for x in re.split(r'[\s,，]+', keywords.strip()) if x}
        expanded = {x.casefold() for x in self.mapping.get(scene, {}).get('keywords', [])}
        ranked = []
        seen = set()
        for item in self.items:
            if item.get('status') != 'active' or item.get('is_mock', True) or not item.get('verified_at'):
                continue
            if not re.fullmatch(r'https://www\.cgltzk\.vip/doc/\d+/', item.get('url', '')):
                continue
            if type and item['type'] != type:
                continue
            if stage and stage not in item['stages']:
                continue
            if industry and industry not in item['industries'] and '通用' not in item['industries']:
                continue
            haystack = ' '.join([item['title'], *item['keywords']]).casefold()
            matches = sorted(t for t in terms if t in haystack)
            # Explicit keywords constrain results; broad scene tags cannot rescue an unrelated query.
            if terms and len(matches) != len(terms):
                continue
            scene_match = bool(scene and scene in item['scenes'])
            mapped = sorted(t for t in expanded if t in haystack)
            if not terms and not scene_match and not mapped:
                continue
            score = 4 * len(matches) + 3 * scene_match + min(len(mapped), 3)
            ranked.append((score, item, matches, mapped, scene_match))
        ranked.sort(key=lambda row: (-row[0], row[1]['id']))
        results = []
        for score, item, matches, mapped, scene_match in ranked:
            if item['url'] in seen:
                continue
            seen.add(item['url'])
            results.append({**item, 'match': {'keywords': matches, 'mapped_keywords': mapped,
                                            'scene': scene_match, 'score': score}})
        return {'schema_version': '1.0', 'source': 'local', 'updated_at': self.updated_at,
                'items': results[:limit], 'total': len(results),
                'warnings': ['仅本地元数据快照；不是全站实时搜索，未验证全文及下载权限。']}


def search_resources(*, provider='local', **query):
    """Stable boundary; HTTP is opt-in and errors do not silently become empty results."""
    if provider == 'local':
        return LocalResourceProvider().search(**query)
    if provider == 'http':
        from http_resources import HttpResourceProvider
        mapping = json.loads((ROOT / 'resource-map.json').read_text(encoding='utf-8'))
        return HttpResourceProvider(mapping).search(**query)
    raise ValueError('provider 必须为 local 或 http')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ('keywords', 'scene', 'stage', 'industry'):
        parser.add_argument('--' + field, default='')
    parser.add_argument('--type', choices=TYPES, default='')
    parser.add_argument('--limit', type=int, default=5)
    parser.add_argument('--provider', choices=('local', 'http'), default='local')
    args = parser.parse_args()
    try:
        result = search_resources(**vars(args))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
