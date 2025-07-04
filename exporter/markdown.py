def tree_to_markdown(directives, level=0):
    lines = []
    prefix = '  ' * level + '- '
    for d in directives:
        if 'block' in d:
            label = f"{d['block']} {d.get('arg') or ''}".strip()
            lines.append(f"{prefix}{label}")
            if d.get('directives'):
                lines.append(tree_to_markdown(d['directives'], level+1))
        elif 'upstream' in d:
            label = f"upstream {d['upstream']}"
            lines.append(f"{prefix}{label}")
            for srv in d.get('servers', []):
                lines.append(f"{'  '*(level+1)}- server {srv}")
        elif 'directive' in d:
            lines.append(f"{prefix}{d['directive']} {d.get('args','')}")
    return '\n'.join(lines) 