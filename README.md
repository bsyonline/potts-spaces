# Potts Spaces

Potts Spaces is a small Python web app that can run locally with the
standard library.

## Local Development

Use Python 3.12 or newer.

Start the local server:

```sh
python -m potts_spaces.app
```

The app listens on `http://127.0.0.1:8000` by default. To use another host or
port, set `HOST` or `PORT` before starting the server.

Run the test suite:

```sh
python -m unittest discover -s tests
```

Expected response examples:

```sh
curl http://127.0.0.1:8000/
```

```json
{"service": "potts-spaces", "status": "ok"}
```

```sh
curl http://127.0.0.1:8000/missing
```

```json
{"error": "not found"}
```
