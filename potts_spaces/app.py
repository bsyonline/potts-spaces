import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def handle_request(path):
    if path == "/":
        return json_response({"service": "potts-spaces", "status": "ok"})

    return json_response({"error": "not found"}, status=404)


def json_response(payload, status=200):
    body = json.dumps(payload).encode("utf-8")
    return status, {"Content-Type": "application/json"}, body


class PottsSpacesHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        status, headers, body = handle_request(self.path)

        self.send_response(status)
        for name, value in headers.items():
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), PottsSpacesHandler)

    print(f"Serving Potts Spaces on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
