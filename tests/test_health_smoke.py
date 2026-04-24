from potts_spaces.app import app


def _call_app(path):
    status_holder = []
    headers_holder = []

    def start_response(status, headers):
        status_holder.append(status)
        headers_holder.extend(headers)

    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": path,
        "SERVER_NAME": "testserver",
        "SERVER_PORT": "80",
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "http",
        "wsgi.input": b"",
        "wsgi.errors": b"",
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
    }

    body = b"".join(app(environ, start_response))
    return status_holder[0], dict(headers_holder), body


def test_health_endpoint_smoke():
    status, headers, body = _call_app("/health")

    assert status == "200 OK"
    assert headers["Content-Type"].startswith("text/plain")
    assert body == b"ok"
