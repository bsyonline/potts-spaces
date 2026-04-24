from wsgiref.util import setup_testing_defaults


def app(environ, start_response):
    setup_testing_defaults(environ)

    if environ.get("PATH_INFO") == "/hello":
        body = b"hello"
        start_response(
            "200 OK",
            [
                ("Content-Type", "text/plain; charset=utf-8"),
                ("Content-Length", str(len(body))),
            ],
        )
        return [body]

    body = b"not found"
    start_response(
        "404 Not Found",
        [
            ("Content-Type", "text/plain; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ],
    )
    return [body]
