from potts_spaces.app import app


def _call_app(path: str):
    status_holder = {}

    def start_response(status, headers):
        status_holder["status"] = status
        status_holder["headers"] = headers

    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": path,
        "SERVER_NAME": "testserver",
        "SERVER_PORT": "80",
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "http",
        "wsgi.input": b"",
        "wsgi.errors": None,
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
    }

    body = b"".join(app(environ, start_response))
    return status_holder["status"], dict(status_holder["headers"]), body


def test_hello_endpoint_smoke():
    status, headers, body = _call_app("/hello")

    assert status == "200 OK"
    assert headers["Content-Type"].startswith("text/plain")
    assert body == b"hello"


def test_health_endpoint():
    status, headers, body = _call_app("/health")

    assert status == "200 OK"
    assert headers["Content-Type"] == "application/json"
    import json
    data = json.loads(body)
    assert data["status"] == "ok"