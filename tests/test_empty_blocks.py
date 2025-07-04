from parser.nginx_parser import parse_nginx_config
from analyzer.empty_blocks import find_empty_blocks
import tempfile
import os

def test_empty_blocks():
    conf = """
    http {
        server {
        }
        upstream backend {
        }
        location / {
            proxy_pass http://backend;
        }
    }
    """
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write(conf)
        f.flush()
        tree = parse_nginx_config(f.name)
    empties = find_empty_blocks(tree)
    # Должны быть пустые server и backend
    assert any(e['block'] == 'server' for e in empties)
    assert any(e['block'] == 'upstream' for e in empties)
    os.unlink(f.name) 
 