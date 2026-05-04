import json
from wsgiref.simple_server import make_server


def application(environ, start_response):
    path = environ.get("PATH_INFO") or "/"
    print(f"request path: {path}")

    if path == "/health":
        body = json.dumps({"status": "ok"}).encode()
        start_response("200 OK", [("Content-Type", "application/json")])
        return [body]

    start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
    return [b"OK\n"]


if __name__ == "__main__":
    with make_server("", 8000, application) as server:
        server.serve_forever()
