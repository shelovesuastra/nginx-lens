from analyzer.base import Analyzer
from typing import List, Dict, Any
import re

def find_rewrite_issues(tree) -> List[Dict[str, Any]]:
    """
    Находит потенциальные проблемы с rewrite: циклы, конфликты, неэффективные правила.
    Возвращает список: [{type, context, value}]
    """
    analyzer = Analyzer(tree)
    issues = []
    rewrites = []
    for d, parent in analyzer.walk():
        if d.get('directive') == 'rewrite':
            args = d.get('args', '')
            parts = args.split()
            if len(parts) >= 2:
                pattern, target = parts[0], parts[1]
                rewrites.append({'pattern': pattern, 'target': target, 'context': parent, 'raw': args})
    # Проверка на циклы (rewrite на себя)
    for r in rewrites:
        if r['pattern'] == r['target']:
            issues.append({'type': 'rewrite_cycle', 'context': r['context'], 'value': r['raw']})
    # Проверка на потенциальные конфликты (два одинаковых паттерна с разными target)
    seen = {}
    for r in rewrites:
        key = r['pattern']
        if key in seen and seen[key] != r['target']:
            issues.append({'type': 'rewrite_conflict', 'context': r['context'], 'value': f"{key} -> {seen[key]} и {key} -> {r['target']}"})
        seen[key] = r['target']
    # Неэффективные rewrite (например, без break/last/redirect/permanent)
    for d, parent in analyzer.walk():
        if d.get('directive') == 'rewrite':
            args = d.get('args', '')
            if not re.search(r'\b(last|break|redirect|permanent)\b', args):
                issues.append({'type': 'rewrite_no_flag', 'context': parent, 'value': args})
    return issues 