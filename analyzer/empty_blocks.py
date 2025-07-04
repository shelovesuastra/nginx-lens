from analyzer.base import Analyzer
from typing import List, Dict, Any

def find_empty_blocks(tree) -> List[Dict[str, Any]]:
    """
    Находит пустые блоки (без вложенных директив).
    Возвращает список: [{block, arg}]
    """
    analyzer = Analyzer(tree)
    empties = []
    for d, parent in analyzer.walk():
        if 'block' in d and (not d.get('directives')):
            empties.append({'block': d.get('block'), 'arg': d.get('arg')})
    return empties 