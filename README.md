# Potts Spaces

A simple Flask application for testing and development workflows.

## Local Development Setup

### Prerequisites

- Python 3.12 or later
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/bsyonline/potts-spaces.git
   cd potts-spaces
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

Start the Flask development server:

```bash
python3 -m flask run --app app
```

Or use Flask's built-in app discovery:

```bash
flask run
```

The application will start on `http://127.0.0.1:5000` by default.

### Expected Responses

#### Health Endpoint

Request:
```bash
curl http://127.0.0.1:5000/health
```

Response:
- Status: `200 OK`
- Body: Empty (no content)

#### Request Logging

Every request path is logged to stdout. For example, a request to `/test-path` will output:

```
/test-path
```

### Running Tests

Run the test suite:

```bash
pytest test_app.py -v
```

Expected output:
```
test_app.py::test_health_endpoint_returns_200 PASSED
test_app.py::test_request_path_is_logged_to_stdout PASSED
```

Both tests should pass, verifying:
- Health endpoint returns HTTP 200
- Request paths are correctly logged to stdout