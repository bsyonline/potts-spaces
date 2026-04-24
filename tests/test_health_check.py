import json
from io import BytesIO
from wsgiref.util import setup_testing_defaults

from app import application


def call_app(path: str, method: str = "GET"):
    environ = {}
    setup_testing_defaults(environ)
    environ["REQUEST_METHOD"] = method
    environ["PATH_INFO"] = path
    environ["wsgi.input"] = BytesIO(b"")

    response = {"status": None, "headers": None}

    def start_response(status, headers):
        response["status"] = status
        response["headers"] = dict(headers)

    body = b"".join(application(environ, start_response))
    return response["status"], response["headers"], body


def test_health_endpoint_smoke():
    status, headers, body = call_app("/health")

    assert status == "200 OK"
    assert headers["Content-Type"] == "application/json"
    assert json.loads(body) == {"status": "healthy"}