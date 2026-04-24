"""Minimal WSGI application for potts-spaces."""

from wsgiref.util import setup_testing_defaults


def app(environ, start_response):
    """WSGI entrypoint with simple route handling."""
    setup_testing_defaults(environ)

    path = environ["PATH_INFO"]
    if path == "/hello":
        body = b"hello"
        status = "200 OK"
        content_type = "text/plain"
    elif path == "/health":
        body = b"ok"
        status = "200 OK"
        content_type = "text/plain"
    else:
        body = b"not found"
        status = "404 Not Found"
        content_type = "text/plain"

    headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(body))),
    ]
    start_response(status, headers)
    return [body]
