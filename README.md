# potts-spaces

A minimal WSGI application with hello and health endpoints.

## Prerequisites

- Python 3.9 or higher

## Setup

1. Clone the repository
2. No additional dependencies required - this is a pure Python WSGI application

## Running Tests

```bash
pytest
```

## Running Locally

The application is a WSGI-compliant Python app. To run it locally for development:

```bash
python -m wsgiref.simple_server src.app:application
```

Or with a custom port:

```bash
python -c "from wsgiref.simple_server import make_server; from app import application; make_server('localhost', 8000, application).serve_forever()"
```

This will start a development server on `http://localhost:8000`.

## Endpoints

- `GET /hello` - Returns `{"message": "hello"}`
- `GET /health` - Returns `{"status": "healthy"}`

## Environment Variables

No environment variables are required for local development.

## Project Structure

```
potts-spaces/
├── src/
│   └── app.py         # Main WSGI application
├── tests/
│   ├── test_hello_endpoint.py
│   └── test_health_check.py
├── pyproject.toml     # Project configuration
└── README.md          # This file
```