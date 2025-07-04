from urllib.parse import urlparse
from analyzer.base import Analyzer
from typing import Dict, Any, Optional
import re

def find_route(tree, url: str) -> Optional[Dict[str, Any]]:
    """
    Находит server и location, которые обслуживают данный URL.
    Возвращает: {'server': ..., 'location': ..., 'proxy_pass': ...}
    """
    parsed = urlparse(url)
    host = parsed.hostname
    port = str(parsed.port or (443 if parsed.scheme == 'https' else 80))
    path = parsed.path or '/'
    analyzer = Analyzer(tree)
    best_server = None
    best_server_score = -1
    # 1. Ищем подходящий server
    for d, _ in analyzer.walk():
        if d.get('block') == 'server':
            names = []
            listens = []
            for sub, _ in analyzer.walk(d['directives'], d):
                if sub.get('directive') == 'server_name':
                    names += sub.get('args', '').split()
                if sub.get('directive') == 'listen':
                    listens.append(sub.get('args', ''))
            score = 0
            if host and any(_host_match(host, n) for n in names):
                score += 2
            if port and any(port in l for l in listens):
                score += 1
            if score > best_server_score:
                best_server = d
                best_server_score = score
    if not best_server or best_server_score < 2:
        return None
    # 2. Внутри server ищем лучший location (longest prefix match)
    best_loc = None
    best_len = -1
    proxy_pass = None
    for sub, _ in analyzer.walk(best_server['directives'], best_server):
        if sub.get('block') == 'location':
            loc = sub.get('arg', '')
            if path.startswith(loc) and len(loc) > best_len:
                best_loc = sub
                best_len = len(loc)
    if best_loc:
        for d, _ in analyzer.walk(best_loc.get('directives', []), best_loc):
            if d.get('directive') == 'proxy_pass':
                proxy_pass = d.get('args')
    return {'server': best_server, 'location': best_loc, 'proxy_pass': proxy_pass}

def _host_match(host, pattern):
    # Примитивная поддержка wildcard
    if pattern == '_':
        return True
    if pattern.startswith('*.'):
        return host.endswith(pattern[1:])
    return host == pattern 