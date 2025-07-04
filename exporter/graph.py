from typing import List

def tree_to_dot(directives) -> str:
    lines = ["digraph nginx {", "  rankdir=LR;"]
    node_id = 0
    def node(label):
        nonlocal node_id
        node_id += 1
        return f"n{node_id}", label
    def walk(dirs, parent_id=None):
        for d in dirs:
            if 'block' in d and d['block'] == 'server':
                nid, label = node(f"server {d.get('arg','')}")
                lines.append(f'  {nid} [label="{label}", shape=box, style=filled, fillcolor=lightblue];')
                if parent_id:
                    lines.append(f'  {parent_id} -> {nid};')
                walk(d.get('directives', []), nid)
            elif 'block' in d and d['block'] == 'location':
                nid, label = node(f"location {d.get('arg','')}")
                lines.append(f'  {nid} [label="{label}", shape=ellipse, style=filled, fillcolor=lightyellow];')
                if parent_id:
                    lines.append(f'  {parent_id} -> {nid};')
                walk(d.get('directives', []), nid)
            elif 'upstream' in d:
                nid, label = node(f"upstream {d['upstream']}")
                lines.append(f'  {nid} [label="{label}", shape=diamond, style=filled, fillcolor=lightgreen];')
                if parent_id:
                    lines.append(f'  {parent_id} -> {nid};')
                for srv in d.get('servers', []):
                    sid, slabel = node(f"server {srv}")
                    lines.append(f'  {sid} [label="{slabel}", shape=note];')
                    lines.append(f'  {nid} -> {sid};')
            elif 'directive' in d and d['directive'] == 'proxy_pass':
                nid, label = node(f"proxy_pass {d.get('args','')}")
                lines.append(f'  {nid} [label="{label}", shape=parallelogram, style=filled, fillcolor=orange];')
                if parent_id:
                    lines.append(f'  {parent_id} -> {nid};')
    walk(directives)
    lines.append("}")
    return '\n'.join(lines)

def tree_to_mermaid(directives) -> str:
    lines = ["graph LR"]
    node_id = 0
    def node(label):
        nonlocal node_id
        node_id += 1
        return f"n{node_id}", label
    def walk(dirs, parent_id=None):
        for d in dirs:
            if 'block' in d and d['block'] == 'server':
                nid, label = node(f"server {d.get('arg','')}")
                lines.append(f'{nid}["{label}"]:::server')
                if parent_id:
                    lines.append(f'{parent_id} --> {nid}')
                walk(d.get('directives', []), nid)
            elif 'block' in d and d['block'] == 'location':
                nid, label = node(f"location {d.get('arg','')}")
                lines.append(f'{nid}["{label}"]:::location')
                if parent_id:
                    lines.append(f'{parent_id} --> {nid}')
                walk(d.get('directives', []), nid)
            elif 'upstream' in d:
                nid, label = node(f"upstream {d['upstream']}")
                lines.append(f'{nid}["{label}"]:::upstream')
                if parent_id:
                    lines.append(f'{parent_id} --> {nid}')
                for srv in d.get('servers', []):
                    sid, slabel = node(f"server {srv}")
                    lines.append(f'{sid}["{slabel}"]:::srv')
                    lines.append(f'{nid} --> {sid}')
            elif 'directive' in d and d['directive'] == 'proxy_pass':
                nid, label = node(f"proxy_pass {d.get('args','')}")
                lines.append(f'{nid}["{label}"]:::proxy')
                if parent_id:
                    lines.append(f'{parent_id} --> {nid}')
    walk(directives)
    # Стили
    lines.append("classDef server fill:#b3e0ff,stroke:#333;")
    lines.append("classDef location fill:#fff2b3,stroke:#333;")
    lines.append("classDef upstream fill:#b3ffb3,stroke:#333;")
    lines.append("classDef proxy fill:#ffd699,stroke:#333;")
    lines.append("classDef srv fill:#eee,stroke:#333;")
    return '\n'.join(lines) 