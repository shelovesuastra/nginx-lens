from parser.nginx_parser import parse_nginx_config
from analyzer.conflicts import find_location_conflicts
import tempfile
import os

def test_location_conflicts():
    conf = """
    server {
        location /api {
            proxy_pass http://backend;
        }
        location /api/v1 {
            proxy_pass http://backend_v1;
        }
        location /static {
            root /var/www/static;
        }
    }
    """
    with tempfile.NamedTemporaryFile("w+", delete=False) as f:
        f.write(conf)
        f.flush()
        tree = parse_nginx_config(f.name)
    conflicts = find_location_conflicts(tree)
    # /api и /api/v1 должны конфликтовать
    assert any("/api" in (c["location1"], c["location2"]) and "/api/v1" in (c["location1"], c["location2"]) for c in conflicts)
    # /static не должен конфликтовать
    assert not any("/static" in (c["location1"], c["location2"]) and ("/api" in (c["location1"], c["location2"]) or "/api/v1" in (c["location1"], c["location2"])) for c in conflicts)
    os.unlink(f.name) 