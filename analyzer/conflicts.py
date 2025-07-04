from analyzer.base import Analyzer
from typing import List, Dict, Any
import re

def find_location_conflicts(tree) -> List[Dict[str, Any]]:
    """
    Находит пересекающиеся location-ы внутри одного server-блока.
    Возвращает список конфликтов: [{server, location1, location2}]
    """
    analyzer = Analyzer(tree)
    conflicts = []
    for d, parent in analyzer.walk():
        if d.get('block') == 'server':
            locations = []
            for sub, _ in analyzer.walk(d['directives'], d):
                if sub.get('block') == 'location':
                    arg = sub.get('arg')
                    if arg:
                        locations.append(arg)
            # Проверяем пересечения
            for i in range(len(locations)):
                for j in range(i+1, len(locations)):
                    if _locations_conflict(locations[i], locations[j]):
                        conflicts.append({
                            'server': d,
                            'location1': locations[i],
                            'location2': locations[j]
                        })
    return conflicts

def _locations_conflict(loc1, loc2):
    # Простая эвристика: если один путь — префикс другого
    return loc1.startswith(loc2) or loc2.startswith(loc1)


def find_listen_servername_conflicts(tree) -> List[Dict[str, Any]]:
    """
    Находит конфликтующие listen/server_name между server-блоками.
    Возвращает список: [{server1, server2, listen, server_name}]
    """
    analyzer = Analyzer(tree)
    servers = []
    for d, parent in analyzer.walk():
        if d.get('block') == 'server':
            listens = set()
            names = set()
            for sub, _ in analyzer.walk(d['directives'], d):
                if sub.get('directive') == 'listen':
                    listens.add(sub.get('args', '').strip())
                if sub.get('directive') == 'server_name':
                    names.update(sub.get('args', '').split())
            servers.append({'block': d, 'listen': listens, 'server_name': names})
    conflicts = []
    for i in range(len(servers)):
        for j in range(i+1, len(servers)):
            common_listen = servers[i]['listen'] & servers[j]['listen']
            common_name = servers[i]['server_name'] & servers[j]['server_name']
            if common_listen and common_name:
                conflicts.append({
                    'server1': servers[i]['block'],
                    'server2': servers[j]['block'],
                    'listen': list(common_listen),
                    'server_name': list(common_name)
                })
    return conflicts 