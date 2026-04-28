# Potts Spaces

A FastAPI application.

## Prerequisites

- Python 3.9 or higher

## Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/bsyonline/potts-spaces.git
cd potts-spaces
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- **Runtime dependencies**: FastAPI, uvicorn
- **Dev dependencies**: pytest, httpx (for testing)

### 4. Run the application

```bash
uvicorn potts_spaces.app:app --reload
```

The server will start at `http://localhost:8000`.

### 5. Run tests

```bash
pytest
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/hello` | GET | Returns a hello message |
| `/health` | GET | Health check endpoint |

## Environment Variables

No environment variables are required for local development at this stage.

## Interactive API Documentation

Once the server is running, access the auto-generated API docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`