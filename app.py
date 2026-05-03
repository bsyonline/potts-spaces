import sys
from flask import Flask, request

app = Flask(__name__)


@app.before_request
def log_request():
    print(request.path, file=sys.stdout)


@app.route('/')
def index():
    return 'Hello'


@app.route('/health')
def health():
    return 'OK'


if __name__ == '__main__':
    app.run()