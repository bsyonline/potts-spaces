import sys
from flask import Flask, request

app = Flask(__name__)


@app.before_request
def log_request_path():
    print(request.path, file=sys.stdout)


@app.route("/health")
def health():
    return "", 200