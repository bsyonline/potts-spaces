# Potts Spaces

A Flask-based REST API for resource management with health monitoring, idempotent creation, and configuration management.

## Local Development

### Prerequisites

- Python 3.12+
- pip

### Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
flask run
```

Or with explicit app specification:

```bash
FLASK_APP=app.py flask run
```

The server starts on `http://localhost:5000` by default.

### Running Tests

Run the full test suite:

```bash
pytest tests/
```

Run with verbose output:

```bash
pytest tests/ -v
```

## API Endpoints

### Health Check

```bash
curl http://localhost:5000/health
```

Response:
```
OK
```

### Liveness Check

```bash
curl http://localhost:5000/live
```

Response:
```json
{
  "status": "ok",
  "uptime_seconds": 12.5,
  "version": "1.0.0",
  "build": "development"
}
```

### Readiness Check

```bash
curl http://localhost:5000/ready
```

Response:
```json
{
  "status": "ok",
  "uptime_seconds": 15.2,
  "version": "1.0.0",
  "build": "development",
  "dependencies": {
    "app": "ok"
  }
}
```

### Create Resource

```bash
curl -X POST http://localhost:5000/resources \
  -H "Content-Type: application/json" \
  -d '{"name": "example", "data": {"key": "value"}}'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "example",
  "data": {"key": "value"}
}
```

### Create Resource with Idempotency

```bash
curl -X POST http://localhost:5000/resources \
  -H "Content-Type: application/json" \
  -H "X-Idempotency-Key: unique-request-key" \
  -d '{"name": "example", "data": {"key": "value"}}'
```

Repeated requests with the same idempotency key return the same response.

### List Resources

```bash
curl http://localhost:5000/resources
```

Response:
```json
{
  "items": [],
  "total": 0,
  "request_id": "abc123"
}
```

With pagination and sorting:

```bash
curl "http://localhost:5000/resources?page=1&per_page=10&sort=name:asc"
```

With filtering:

```bash
curl "http://localhost:5000/resources?filter=name:example*"
```

### Get Configuration

```bash
curl http://localhost:5000/admin/config
```

Response:
```json
{
  "config": {
    "max_requests_per_second": 50,
    "timeout_seconds": 10,
    "feature_flags": {}
  }
}
```

### Reload Configuration

```bash
curl -X POST http://localhost:5000/admin/config/reload \
  -H "Content-Type: application/json" \
  -d '{"config": {"max_requests_per_second": 100}}'
```

Response:
```json
{
  "status": "success",
  "config": {
    "max_requests_per_second": 100,
    "timeout_seconds": 10,
    "feature_flags": {}
  }
}
```