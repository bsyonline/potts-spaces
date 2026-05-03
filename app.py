from flask import Flask, request
import sys

app = Flask(__name__)

@app.before_request
def log_request_path():
    print(request.path, file=sys.stdout)

@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run()