import socket
from typing import Dict, List

def check_upstreams(upstreams: Dict[str, List[str]], timeout=2.0, retries=1):
    # TODO: Реализовать реальную проверку TCP/HTTP
    # Сейчас возвращает все healthy
    result = {}
    for name, servers in upstreams.items():
        result[name] = []
        for srv in servers:
            result[name].append({"address": srv, "healthy": True})
    return result 