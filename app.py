import time
from flask import Flask, request, jsonify

app = Flask(__name__)
START_TIME = time.time()
VERSION = '1.0.0'
BUILD = 'development'


@app.before_request
def log_request():
    print(request.path)


def get_uptime_seconds():
    return time.time() - START_TIME


def make_health_response():
    return {
        'status': 'ok',
        'uptime_seconds': get_uptime_seconds(),
        'version': VERSION,
        'build': BUILD
    }


@app.route('/health')
def health():
    return 'OK', 200


@app.route('/live')
def live():
    return jsonify(make_health_response()), 200


@app.route('/ready')
def ready():
    response = make_health_response()
    response['dependencies'] = {
        'app': 'ok'
    }
    return jsonify(response), 200