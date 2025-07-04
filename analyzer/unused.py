from analyzer.base import Analyzer
from typing import List, Dict, Any
import re

def find_unused_variables(tree) -> List[Dict[str, Any]]:
    """
    Находит переменные, определённые через set/map, которые не используются.
    Возвращает список: [{name, context}]
    """
    analyzer = Analyzer(tree)
    defined = set()
    used = set()
    for d, parent in analyzer.walk():
        if d.get('directive') == 'set':
            parts = d.get('args', '').split()
            if parts:
                defined.add(parts[0])
        if d.get('directive') == 'map':
            parts = d.get('args', '').split()
            if parts:
                defined.add(parts[0])
        # Ищем использование $var в любых аргументах
        for v in re.findall(r'\$[a-zA-Z0-9_]+', str(d.get('args',''))):
            used.add(v)
    unused = []
    for var in defined:
        if var not in used:
            unused.append({'name': var, 'context': None})
    return unused 