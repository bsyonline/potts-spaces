import contextlib
import io
import json
import unittest
from pathlib import Path

from potts_spaces.app import PottsSpacesHandler, handle_request


class LocalStartupDocumentationTests(unittest.TestCase):
    def test_home_response_matches_readme_example(self):
        status, headers, body = handle_request("/")

        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(
            json.loads(body.decode("utf-8")),
            {"service": "potts-spaces", "status": "ok"},
        )

    def test_unknown_path_returns_not_found_json(self):
        status, headers, body = handle_request("/missing")

        self.assertEqual(status, 404)
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(json.loads(body.decode("utf-8")), {"error": "not found"})

    def test_get_request_logs_incoming_path_to_stdout(self):
        handler = object.__new__(PottsSpacesHandler)
        handler.path = "/missing?debug=true"
        handler.wfile = io.BytesIO()
        responses = []
        headers = []
        handler.send_response = responses.append
        handler.send_header = lambda name, value: headers.append((name, value))
        handler.end_headers = lambda: None

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            PottsSpacesHandler.do_GET(handler)

        self.assertIn("/missing?debug=true", stdout.getvalue())
        self.assertEqual(responses, [404])
        self.assertIn(("Content-Type", "application/json"), headers)
        self.assertEqual(json.loads(handler.wfile.getvalue().decode("utf-8")), {"error": "not found"})

    def test_readme_documents_local_startup(self):
        readme = Path("README.md").read_text(encoding="utf-8")

        self.assertIn("python -m potts_spaces.app", readme)
        self.assertIn("python -m unittest discover -s tests", readme)
        self.assertIn("curl http://127.0.0.1:8000/", readme)
        self.assertIn("curl http://127.0.0.1:8000/missing", readme)
        self.assertIn('{"service": "potts-spaces", "status": "ok"}', readme)
        self.assertIn('{"error": "not found"}', readme)


if __name__ == "__main__":
    unittest.main()
