import json
import unittest
from pathlib import Path

from potts_spaces.app import handle_request


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
