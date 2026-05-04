import unittest
from pathlib import Path


class ReadmeStartupDocsTests(unittest.TestCase):
    def test_readme_documents_local_startup(self):
        readme = Path("README.md")
        self.assertTrue(readme.exists(), "README.md should document local startup")

        content = readme.read_text(encoding="utf-8")

        self.assertIn("python3 app.py", content)
        self.assertIn("python3 -m unittest discover -s tests", content)
        self.assertIn("curl -i http://127.0.0.1:8000/", content)
        self.assertIn("HTTP/1.0 200 OK", content)
        self.assertIn("OK", content)
        self.assertIn("request path: /debug/path", content)


if __name__ == "__main__":
    unittest.main()
