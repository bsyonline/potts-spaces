import json
import unittest

from app import application


class HealthCheckTests(unittest.TestCase):
    def _call(self, path):
        environ = {"PATH_INFO": path}
        status_headers = []

        def start_response(status, headers):
            status_headers.append((status, headers))

        body = b"".join(application(environ, start_response))
        return status_headers[0][0], status_headers[0][1], body

    def test_health_returns_200(self):
        status, _, _ = self._call("/health")
        self.assertEqual("200 OK", status)

    def test_health_returns_json_ok(self):
        _, headers, body = self._call("/health")
        content_types = [v for k, v in headers if k == "Content-Type"]
        self.assertTrue(any("application/json" in ct for ct in content_types))
        data = json.loads(body.decode())
        self.assertEqual({"status": "ok"}, data)


if __name__ == "__main__":
    unittest.main()
