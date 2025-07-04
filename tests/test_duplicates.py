from parser.nginx_parser import parse_nginx_config
from analyzer.duplicates import find_duplicate_directives
import tempfile
import os

def test_duplicate_directives():
    conf = """
    server {
        listen 80;
        listen 80;
        server_name example.com;
        server_name example.com;
        location / {
            proxy_pass http://backend;
            proxy_pass http://backend;
        }
    }
    """
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write(conf)
        f.flush()
        tree = parse_nginx_config(f.name)
    dups = find_duplicate_directives(tree)
    assert any(d['directive'] == 'listen' and d['count'] == 2 for d in dups)
    assert any(d['directive'] == 'server_name' and d['count'] == 2 for d in dups)
    assert any(d['directive'] == 'proxy_pass' and d['count'] == 2 for d in dups)
    os.unlink(f.name) 