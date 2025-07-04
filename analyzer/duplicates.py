from analyzer.base import Analyzer
from typing import List, Dict, Any

def find_duplicate_directives(tree) -> List[Dict[str, Any]]:
    """
    Находит дублирующиеся директивы внутри одного блока (без вложенности).
    Возвращает список: [{block, directive, count, location}]
    """
    analyzer = Analyzer(tree)
    duplicates = []
    for d, parent in analyzer.walk():
        if 'directives' in d:
            # Считаем только прямые дочерние директивы (без вложенных блоков)
            seen = {}
            for sub in d['directives']:
                if 'directive' in sub:
                    key = (sub['directive'], str(sub.get('args')))
                    seen[key] = seen.get(key, 0) + 1
            for (directive, args), count in seen.items():
                if count > 1:
                    duplicates.append({
                        'block': d,
                        'directive': directive,
                        'args': args,
                        'count': count,
                        'location': d.get('arg')
                    })
    return duplicates 