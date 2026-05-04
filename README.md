# potts-spaces

## Local Development

### Prerequisites

- Python 3.x

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start the App

```bash
python app.py
```

The server starts on `http://localhost:5000` by default.

### Run Tests

```bash
pytest
```

### Expected Responses

**Health check**

```
GET /health

HTTP/1.1 200 OK
(empty body)
```
