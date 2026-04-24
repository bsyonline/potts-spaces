from __future__ import annotations

from io import BytesIO
from wsgiref.util import setup_testing_defaults

from app import app


def _call_app(method: str, path: str):
    environ = {}
    setup_testing_defaults(environ)
    environ["REQUEST_METHOD"] = method
    environ["PATH_INFO"] = path
    environ["wsgi.input"] = BytesIO()

    state = {}

    def start_response(status, headers):
        state["status"] = status
        state["headers"] = dict(headers)

    body = b"".join(app(environ, start_response))
    return state["status"], state["headers"], body


def test_hello_endpoint_smoke():
    status, headers, body = _call_app("GET", "/hello")

    assert status == "200 OK"
    assert headers["Content-Type"] == "application/json; charset=utf-8"
    assert body == b'{"message":"hello"}\n'
