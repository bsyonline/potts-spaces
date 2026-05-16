from flask import Flask, request

app = Flask(__name__)


@app.before_request
def log_request():
    print(request.path)


@app.route('/health')
def health():
    return 'OK', 200