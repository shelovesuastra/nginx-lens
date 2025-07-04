def tree_to_html(directives, level=0):
    html = []
    html.append('<ul>')
    for d in directives:
        if 'block' in d:
            label = f"{d['block']} {d.get('arg') or ''}".strip()
            html.append(f"<li><b>{label}</b>")
            if d.get('directives'):
                html.append(tree_to_html(d['directives'], level+1))
            html.append("</li>")
        elif 'upstream' in d:
            label = f"upstream {d['upstream']}"
            html.append(f"<li><b>{label}</b><ul>")
            for srv in d.get('servers', []):
                html.append(f"<li>server {srv}</li>")
            html.append("</ul></li>")
        elif 'directive' in d:
            html.append(f"<li>{d['directive']} {d.get('args','')}</li>")
    html.append('</ul>')
    return '\n'.join(html) 