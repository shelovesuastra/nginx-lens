import os
import glob
from typing import Dict, List, Any
import re

class NginxConfigTree:
    def __init__(self, directives=None, upstreams=None):
        self.directives = directives or []
        self._upstreams = upstreams or {}
    def get_upstreams(self) -> Dict[str, List[str]]:
        return self._upstreams

# --- Вспомогательные функции ---
def _strip_comments(line: str) -> str:
    return line.split('#', 1)[0].strip()

def _parse_block(lines, base_dir, source_file=None) -> (List[Any], Dict[str, List[str]]):
    directives = []
    upstreams = {}
    i = 0
    while i < len(lines):
        line = _strip_comments(lines[i])
        if not line:
            i += 1
            continue
        if line.startswith('include '):
            pattern = line[len('include '):].rstrip(';').strip()
            pattern = os.path.join(base_dir, pattern) if not os.path.isabs(pattern) else pattern
            for inc_path in glob.glob(pattern):
                with open(inc_path) as f:
                    inc_lines = f.readlines()
                inc_directives, inc_upstreams = _parse_block(inc_lines, os.path.dirname(inc_path), inc_path)
                directives.extend(inc_directives)
                for k, v in inc_upstreams.items():
                    upstreams.setdefault(k, []).extend(v)
            i += 1
            continue
        m = re.match(r'upstream\s+(\S+)\s*{', line)
        if m:
            name = m.group(1)
            block_lines = []
            depth = 1
            i += 1
            while i < len(lines) and depth > 0:
                l = _strip_comments(lines[i])
                if '{' in l:
                    depth += l.count('{')
                if '}' in l:
                    depth -= l.count('}')
                if depth > 0:
                    block_lines.append(l)
                i += 1
            servers = []
            for bl in block_lines:
                m_srv = re.match(r'server\s+([^;]+);', bl)
                if m_srv:
                    servers.append(m_srv.group(1).strip())
            upstreams[name] = servers
            directives.append({'upstream': name, 'servers': servers, '__file__': source_file})
            continue
        # Блоки (например, server, http, location)
        m = re.match(r'(\S+)\s*(\S+)?\s*{', line)
        if m:
            block_name = m.group(1)
            block_arg = m.group(2)
            block_lines = []
            depth = 1
            i += 1
            while i < len(lines) and depth > 0:
                l = _strip_comments(lines[i])
                if '{' in l:
                    depth += l.count('{')
                if '}' in l:
                    depth -= l.count('}')
                if depth > 0:
                    block_lines.append(l)
                i += 1
            sub_directives, sub_upstreams = _parse_block(block_lines, base_dir, source_file)
            directives.append({'block': block_name, 'arg': block_arg, 'directives': sub_directives, '__file__': source_file})
            for k, v in sub_upstreams.items():
                upstreams.setdefault(k, []).extend(v)
            continue
        # Обычная директива
        m = re.match(r'(\S+)\s+([^;]+);', line)
        if m:
            directives.append({'directive': m.group(1), 'args': m.group(2), '__file__': source_file})
        i += 1
    return directives, upstreams

def parse_nginx_config(path: str) -> NginxConfigTree:
    base_dir = os.path.dirname(os.path.abspath(path))
    with open(path) as f:
        lines = f.readlines()
    directives, upstreams = _parse_block(lines, base_dir, path)
    return NginxConfigTree(directives, upstreams) 