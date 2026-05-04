# Potts Spaces

## Local Development

This app runs with Python's standard library. From the repository root, run the
test suite first:

```sh
python3 -m unittest discover -s tests
```

Start the local web server:

```sh
python3 app.py
```

The app listens on `http://127.0.0.1:8000/`. In another terminal, verify the
server response:

```sh
curl -i http://127.0.0.1:8000/
```

Expected response:

```http
HTTP/1.0 200 OK
Content-Type: text/plain; charset=utf-8

OK
```

Any path returns the same response body and logs the requested path in the server
terminal:

```sh
curl http://127.0.0.1:8000/debug/path
```

Expected response body:

```text
OK
```

Expected server log:

```text
request path: /debug/path
```

Stop the server with `Ctrl-C`.
