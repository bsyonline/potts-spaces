"""Minimal WSGI application exposing a hello endpoint."""

from __future__ import annotations

from typing import Iterable


ResponseBody = Iterable[bytes]


def app(environ: dict, start_response) -> ResponseBody:
    """Serve a small HTTP API.

    - GET /hello -> 200 {"message":"hello"}
    - anything else -> 404
    """
    method = environ.get("REQUEST_METHOD", "")
    path = environ.get("PATH_INFO", "")

    if method == "GET" and path == "/hello":
        status = "200 OK"
        payload = b'{"message":"hello"}\n'
        headers = [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(payload))),
        ]
        start_response(status, headers)
        return [payload]

    status = "404 Not Found"
    payload = b'{"error":"not found"}\n'
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(payload))),
    ]
    start_response(status, headers)
    return [payload]


if __name__ == "__main__":
    from wsgiref.simple_server import make_server

    with make_server("127.0.0.1", 8000, app) as server:
        server.serve_forever()
