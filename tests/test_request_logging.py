import io
import unittest
from contextlib import redirect_stdout

from app import application


class RequestLoggingTests(unittest.TestCase):
    def test_application_logs_incoming_path(self):
        environ = {"PATH_INFO": "/debug/path"}
        status_headers = []

        def start_response(status, headers):
            status_headers.append((status, headers))

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            body = b"".join(application(environ, start_response))

        self.assertIn("/debug/path", stdout.getvalue())
        self.assertEqual("200 OK", status_headers[0][0])
        self.assertEqual(b"OK\n", body)


if __name__ == "__main__":
    unittest.main()
