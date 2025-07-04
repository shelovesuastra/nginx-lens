from typing import List, Dict, Any

def diff_trees(tree1, tree2) -> List[Dict[str, Any]]:
    """
    Сравнивает два дерева директив. Возвращает список отличий.
    Формат: [{type, path, value1, value2}]
    type: 'added', 'removed', 'changed'
    path: путь до директивы (например, ['http', 'server', 'location /api'])
    """
    diffs = []
    _diff_blocks(tree1.directives, tree2.directives, [], diffs)
    return diffs

def _diff_blocks(d1, d2, path, diffs):
    # Индексируем по (block,arg) или (directive,args) или (upstream)
    def key(d):
        if 'block' in d:
            return ('block', d['block'], d.get('arg'))
        if 'directive' in d:
            return ('directive', d['directive'], d.get('args'))
        if 'upstream' in d:
            return ('upstream', d['upstream'])
        return ('other', str(d))
    map1 = {key(x): x for x in d1}
    map2 = {key(x): x for x in d2}
    all_keys = set(map1) | set(map2)
    for k in all_keys:
        v1 = map1.get(k)
        v2 = map2.get(k)
        p = path + [k[1] if k[0] != 'directive' else f"{k[1]} {k[2] or ''}".strip()]
        if v1 and not v2:
            diffs.append({'type': 'removed', 'path': p, 'value1': v1, 'value2': None})
        elif v2 and not v1:
            diffs.append({'type': 'added', 'path': p, 'value1': None, 'value2': v2})
        else:
            # Рекурсивно сравниваем блоки
            if 'directives' in v1 and 'directives' in v2:
                _diff_blocks(v1['directives'], v2['directives'], p, diffs)
            elif v1 != v2:
                diffs.append({'type': 'changed', 'path': p, 'value1': v1, 'value2': v2}) 