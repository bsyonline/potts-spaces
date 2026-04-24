import json
from typing import Callable, Iterable, List, Tuple

StartResponse = Callable[[str, List[Tuple[str, str]]], None]


def application(environ: dict, start_response: StartResponse) -> Iterable[bytes]:
    method = environ.get("REQUEST_METHOD", "")
    path = environ.get("PATH_INFO", "")

    if method == "GET" and path == "/hello":
        payload = json.dumps({"message": "hello"}).encode("utf-8")
        headers = [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(payload))),
        ]
        start_response("200 OK", headers)
        return [payload]

    if method == "GET" and path == "/health":
        payload = json.dumps({"status": "healthy"}).encode("utf-8")
        headers = [
            ("Content-Type", "application/json"),
            ("Content-Length", str(len(payload))),
        ]
        start_response("200 OK", headers)
        return [payload]

    payload = json.dumps({"error": "not found"}).encode("utf-8")
    headers = [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(payload))),
    ]
    start_response("404 Not Found", headers)
    return [payload]
