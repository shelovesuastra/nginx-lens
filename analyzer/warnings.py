from analyzer.base import Analyzer
from typing import List, Dict, Any
import re

# Список устаревших директив (пример)
DEPRECATED_DIRECTIVES = {
    'ssl': 'ssl директива устарела, используйте listen ... ssl',
    'spdy': 'spdy устарел, используйте http2',
    'ssl_session_cache': 'ssl_session_cache устарел в новых версиях',
}

# Список security-заголовков
SECURITY_HEADERS = [
    'X-Frame-Options',
    'Strict-Transport-Security',
    'X-Content-Type-Options',
    'Referrer-Policy',
    'Content-Security-Policy',
]

LIMITS = {
    'client_max_body_size': {'min': 1024*1024, 'max': 1024*1024*100},  # 1M - 100M
    'proxy_buffer_size': {'min': 4096, 'max': 1024*1024},             # 4K - 1M
    'proxy_buffers': {'min': 2, 'max': 32},                           # 2-32
    'proxy_busy_buffers_size': {'min': 4096, 'max': 1024*1024},       # 4K - 1M
}

def _parse_size(val):
    # Преобразует строку типа 1m, 512k, 4096 в байты
    val = val.strip().lower()
    if val.endswith('k'):
        return int(float(val[:-1]) * 1024)
    if val.endswith('m'):
        return int(float(val[:-1]) * 1024 * 1024)
    try:
        return int(val)
    except Exception:
        return None

def find_warnings(tree) -> List[Dict[str, Any]]:
    """
    Находит потенциально опасные или неочевидные директивы и нарушения best practices.
    Возвращает список: [{type, directive, context, value}]
    """
    analyzer = Analyzer(tree)
    warnings = []
    found_headers = set()
    for d, parent in analyzer.walk():
        # proxy_pass без схемы
        if d.get('directive') == 'proxy_pass':
            val = d.get('args', '')
            if not re.match(r'^(http|https)://', val):
                warnings.append({'type': 'proxy_pass_no_scheme', 'directive': 'proxy_pass', 'context': parent, 'value': val})
        # autoindex on
        if d.get('directive') == 'autoindex' and d.get('args', '').strip() == 'on':
            warnings.append({'type': 'autoindex_on', 'directive': 'autoindex', 'context': parent, 'value': 'on'})
        # if внутри блока
        if d.get('block') == 'if':
            warnings.append({'type': 'if_block', 'directive': 'if', 'context': parent, 'value': ''})
        # server_tokens on
        if d.get('directive') == 'server_tokens' and d.get('args', '').strip() == 'on':
            warnings.append({'type': 'server_tokens_on', 'directive': 'server_tokens', 'context': parent, 'value': 'on'})
        # ssl_certificate/ssl_certificate_key
        if d.get('directive') == 'ssl_certificate' or d.get('directive') == 'ssl_certificate_key':
            if not d.get('args', '').strip():
                warnings.append({'type': 'ssl_missing', 'directive': d['directive'], 'context': parent, 'value': ''})
        # ssl_protocols
        if d.get('directive') == 'ssl_protocols':
            val = d.get('args', '')
            if 'TLSv1' in val or 'TLSv1.1' in val:
                warnings.append({'type': 'ssl_protocols_weak', 'directive': 'ssl_protocols', 'context': parent, 'value': val})
        # ssl_ciphers
        if d.get('directive') == 'ssl_ciphers':
            val = d.get('args', '')
            if any(x in val for x in ['RC4', 'MD5', 'DES']):
                warnings.append({'type': 'ssl_ciphers_weak', 'directive': 'ssl_ciphers', 'context': parent, 'value': val})
        # listen 443 ssl
        if d.get('directive') == 'listen' and '443' in d.get('args', '') and 'ssl' not in d.get('args', ''):
            warnings.append({'type': 'listen_443_no_ssl', 'directive': 'listen', 'context': parent, 'value': d.get('args', '')})
        # http2
        if d.get('directive') == 'listen' and '443' in d.get('args', '') and 'http2' not in d.get('args', ''):
            warnings.append({'type': 'listen_443_no_http2', 'directive': 'listen', 'context': parent, 'value': d.get('args', '')})
        # limit_req/limit_conn
        if d.get('block') == 'server':
            has_limit = False
            for sub, _ in analyzer.walk(d.get('directives', []), d):
                if sub.get('directive') in ('limit_req', 'limit_conn'):
                    has_limit = True
            if not has_limit:
                warnings.append({'type': 'no_limit_req_conn', 'directive': 'server', 'context': d, 'value': ''})
        # Security headers
        if d.get('directive') == 'add_header':
            for h in SECURITY_HEADERS:
                if h in d.get('args', ''):
                    found_headers.add(h)
        # Deprecated directives
        if d.get('directive') in DEPRECATED_DIRECTIVES:
            warnings.append({'type': 'deprecated', 'directive': d['directive'], 'context': parent, 'value': DEPRECATED_DIRECTIVES[d['directive']]})
        # Проверка лимитов и буферов
        for lim, rng in LIMITS.items():
            if d.get('directive') == lim:
                val = d.get('args', '').split()[0]
                size = _parse_size(val)
                if size is not None:
                    if size < rng['min']:
                        warnings.append({'type': 'limit_too_small', 'directive': lim, 'context': parent, 'value': val})
                    if size > rng['max']:
                        warnings.append({'type': 'limit_too_large', 'directive': lim, 'context': parent, 'value': val})
    # Проверка отсутствующих security headers
    for h in SECURITY_HEADERS:
        if h not in found_headers:
            warnings.append({'type': 'missing_security_header', 'directive': 'add_header', 'context': None, 'value': h})
    return warnings 