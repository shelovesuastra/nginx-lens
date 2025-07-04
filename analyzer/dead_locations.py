from analyzer.base import Analyzer
from typing import List, Dict, Any, Set
import re

def find_dead_locations(tree) -> List[Dict[str, Any]]:
    """
    Находит location-ы, которые не используются ни в одном proxy_pass, rewrite, try_files и т.д.
    Возвращает список: [{server, location}]
    """
    analyzer = Analyzer(tree)
    locations = []
    used = set()
    # Собираем все location
    for d, parent in analyzer.walk():
        if d.get('block') == 'server':
            for sub, _ in analyzer.walk(d.get('directives', []), d):
                if sub.get('block') == 'location':
                    locations.append({'server': d, 'location': sub})
    # Собираем все использования location (proxy_pass, rewrite, try_files)
    for d, parent in analyzer.walk():
        for key in ('proxy_pass', 'rewrite', 'try_files'):
            if d.get('directive') == key:
                args = d.get('args', '')
                for l in locations:
                    loc = l['location'].get('arg', '')
                    if loc and loc in args:
                        used.add((l['server'].get('arg',''), loc))
    # Те, что не используются
    dead = []
    for l in locations:
        key = (l['server'].get('arg',''), l['location'].get('arg',''))
        if key not in used:
            dead.append(l)
    return dead 