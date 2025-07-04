import os
import glob
from typing import List, Dict, Any, Set

def build_include_tree(path: str, visited: Set[str]=None) -> Dict[str, Any]:
    """
    Строит дерево include-ов начиная с path. Возвращает dict: {file: [subincludes]}
    """
    if visited is None:
        visited = set()
    path = os.path.abspath(path)
    if path in visited:
        return {path: 'cycle'}
    visited.add(path)
    includes = []
    try:
        with open(path) as f:
            lines = f.readlines()
    except Exception:
        return {path: 'not_found'}
    for line in lines:
        line = line.split('#', 1)[0].strip()
        if line.startswith('include '):
            pattern = line[len('include '):].rstrip(';').strip()
            pattern = os.path.join(os.path.dirname(path), pattern) if not os.path.isabs(pattern) else pattern
            for inc_path in glob.glob(pattern):
                includes.append(build_include_tree(inc_path, visited.copy()))
    return {path: includes}

def find_include_cycles(tree: Dict[str, Any], stack=None) -> List[List[str]]:
    """
    Находит циклы include-ов в дереве. Возвращает список путей.
    """
    if stack is None:
        stack = []
    cycles = []
    for k, v in tree.items():
        if v == 'cycle':
            cycles.append(stack + [k])
        elif isinstance(v, list):
            for sub in v:
                if isinstance(sub, dict):
                    cycles.extend(find_include_cycles(sub, stack + [k]))
    return cycles

def find_include_shadowing(tree: Dict[str, Any], directive: str) -> List[Dict[str, Any]]:
    """
    Находит переопределения директивы в разных include-ах.
    Возвращает список: [{file, directive, value}]
    """
    found = []
    def _walk(t):
        for k, v in t.items():
            if isinstance(v, list):
                # Проверяем сам файл
                try:
                    with open(k) as f:
                        for line in f:
                            if line.strip().startswith(directive + ' '):
                                found.append({'file': k, 'directive': directive, 'value': line.strip()})
                except Exception:
                    pass
                for sub in v:
                    if isinstance(sub, dict):
                        _walk(sub)
    _walk(tree)
    return found 