# Potts Spaces

A simple Python WSGI application with a health check endpoint.

## Local Development Startup

### Prerequisites

- Python 3.12 or higher
- pytest (for running tests)
- gunicorn (for running the application server)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd potts-spaces
   ```

2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

### Running Tests

Run the test suite using pytest:

```bash
pytest tests/ -v
```

Expected output:
```
tests/test_health.py::test_health_endpoint_returns_200 PASSED [100%]
============================== 1 passed in 0.08s ===============================
```

### Starting the Application

Start the application server using gunicorn:

```bash
gunicorn --bind localhost:8000 potts_spaces.app:app
```

The server will start and listen at `http://localhost:8000`.

Alternatively, you can use Python's built-in WSGI server:

```bash
python -m wsgiref.simple_server
```

Then import and run the app manually (see the wsgiref documentation).

### Expected Responses

#### Health Endpoint

**Request:**
```bash
curl http://localhost:8000/health
```

**Response:**
- Status: `200 OK`
- Body: `OK`
- Content-Type: `text/plain; charset=utf-8`

#### Other Endpoints

**Request:**
```bash
curl http://localhost:8000/other
```

**Response:**
- Status: `404 Not Found`
- Body: `not found`
- Content-Type: `text/plain; charset=utf-8`

## Project Structure

```
potts-spaces/
├── potts_spaces/
│   └── app.py          # WSGI application
├── tests/
│   └── test_health.py  # Health endpoint tests
├── setup.py            # Package setup
└── README.md           # This file
```

## Development Workflow

1. Make code changes
2. Run tests to verify changes: `pytest tests/ -v`
3. Start the server to test manually: `gunicorn --bind localhost:8000 potts_spaces.app:app`
4. Commit changes when tests pass