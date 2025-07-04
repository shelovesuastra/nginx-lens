from typing import Any, List, Dict

class Analyzer:
    def __init__(self, tree):
        self.tree = tree
        self.directives = tree.directives

    def walk(self, directives=None, parent=None):
        """
        Рекурсивно обходит дерево директив.
        Возвращает генератор (директива, родитель).
        """
        if directives is None:
            directives = self.directives
        for d in directives:
            yield d, parent
            if 'directives' in d:
                yield from self.walk(d['directives'], d) 