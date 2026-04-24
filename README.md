# potts-spaces

## Local development startup

### Prerequisites

- Python 3.11+ (3.12 recommended)

### 1) Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip pytest
```

### 2) Run the smoke tests

```bash
pytest -q
```

Expected: both smoke tests pass (`/hello` and `/health`).

### 3) Start the app locally

```bash
python -c "from wsgiref.simple_server import make_server; from potts_spaces.app import app; make_server('127.0.0.1', 8000, app).serve_forever()"
```

### 4) Verify endpoints

In another terminal:

```bash
curl -i http://127.0.0.1:8000/hello
curl -i http://127.0.0.1:8000/health
```

Expected response bodies:

- `/hello` -> `hello`
- `/health` -> `ok`

### 5) Stop the server

Press `Ctrl+C` in the server terminal.
