from flask import Flask, request

app = Flask(__name__)


@app.before_request
def log_request():
    print(request.path)


@app.route('/')
def index():
    return 'Hello'


@app.route('/test-path')
def test_path():
    return 'Test'


if __name__ == '__main__':
    app.run()