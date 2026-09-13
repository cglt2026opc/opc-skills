"""Adapter for the existing public cgltzk keyword endpoint (opt-in network access)."""
import json
import re
from datetime import datetime, timezone
from html import unescape
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ENDPOINT = 'https://api.cgltzk.vip/mapp/search/'


def plain(value):
    return unescape(re.sub(r'<[^>]*>', '', str(value or ''))).strip()


def infer_type(title):
    # Title-derived hints, not server classifications or full-text verification.
    for kind, words in [('report', ('报告', '白皮书')), ('worksheet', ('自检表', '工具表', '测评表')),
                        ('template', ('模板', '模版')), ('case', ('案例',)),
                        ('tutorial', ('教程', '方法论', '指南')), ('plan', ('方案',)),
                        ('collection', ('资料集', '专题'))]:
        if any(word in title for word in words):
            return kind
    return 'unknown'


class HttpResourceProvider:
    def __init__(self, mapping, opener=urlopen):
        self.mapping = mapping
        self.opener = opener

    def search(self, *, keywords='', scene='', stage='', type='', limit=5, industry=''):
        from query_resources import TYPES
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 5:
            raise ValueError('limit 必须为 1～5')
        if type and type not in TYPES:
            raise ValueError('不支持的资源类型')
        if scene and scene not in self.mapping:
            raise ValueError('未知 scene；请使用模块名或留空')
        if len(keywords) > 200:
            raise ValueError('keywords 最多 200 字符')
        terms = [x for x in re.split(r'[\s,，]+', keywords.strip()) if x]
        if len(terms) > 10:
            raise ValueError('keywords 最多 10 个主题词')
        # Bound requests: one precise keyword query, then locally enforce all terms.
        term = terms[0] if terms else next(iter(self.mapping.get(scene, {}).get('keywords', [])), '')
        warnings = ['在线搜索元数据；未读取全文或验证下载权限。类型由标题推断，须复核。',
                    '仅取第 1 页最多 50 条候选，total 是本页过滤后数量，不代表全站匹配数。']
        if stage or industry:
            warnings.append('接口不提供 OPC 阶段/行业标签；stage/industry 未自动过滤，须按用户场景人工复核。')
        result = {'schema_version': '1.0', 'source': 'http', 'updated_at': None,
                  'items': [], 'total': 0, 'warnings': warnings}
        if not term:
            return result
        params = {'model_id': 4, 'kw': term, 'page': 1, 'pageSize': 50}
        request = Request(ENDPOINT + '?' + urlencode(params), headers={'Accept': 'application/json', 'User-Agent': 'opc-skills/0.3'})
        with self.opener(request, timeout=5) as response:
            raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError('API 响应超过大小限制')
        payload = json.loads(raw)
        if not isinstance(payload, dict) or payload.get('error') != 0 or payload.get('code') != 200:
            raise ValueError('API 返回非成功状态')
        data = payload.get('data')
        if not isinstance(data, dict) or not isinstance(data.get('resultList'), list):
            raise ValueError('API 返回结构不符合 resultList 契约')
        if len(data['resultList']) > 50:
            raise ValueError('API 返回超出请求数量')
        now = datetime.now(timezone.utc).isoformat()
        result.update(updated_at=now, upstream_count=data.get('count'), query_keyword=term)
        seen = set()
        for row in data['resultList']:
            if not isinstance(row, dict):
                raise ValueError('API 资源条目不是对象')
            id = str(row.get('id', ''))
            if not re.fullmatch(r'[0-9]+', id) or id in seen:
                continue
            if str(row.get('is_delete', '1')) != '0' or str(row.get('status', '0')) != '1' or str(row.get('is_link', '1')) != '0':
                continue
            title = plain(row.get('title'))
            tags = plain(row.get('tags'))
            if not title:
                continue
            haystack = (title + ' ' + tags + ' ' + plain(row.get('keywords'))).casefold()
            if not all(t.casefold() in haystack for t in (terms or [term])):
                continue
            kind = infer_type(title)
            if type and kind != type:
                continue
            seen.add(id)
            result['items'].append({
                'id': 'cgltzk-' + id, 'title': title,
                'url': 'https://www.cgltzk.vip/doc/' + id + '/',
                'type': kind, 'type_basis': 'title_inference', 'format': plain(row.get('ext')),
                'keywords': [x for x in re.split(r'[,，]', tags) if x],
                'scenes': [], 'stages': [], 'industries': [],
                'purpose': '', 'suitable_for': '',
                'verified_at': now, 'verification': 'api_metadata',
                'access': '下载与会员权限以详情页及登录后为准；不根据单个价格字段判断免费',
                'status': 'active', 'is_mock': False,
                'match': {'keywords': terms or [term], 'scene': False, 'mapped_keywords': [] if terms else [term]},
            })
        result['total'] = len(result['items'])
        result['items'] = result['items'][:limit]
        return result
