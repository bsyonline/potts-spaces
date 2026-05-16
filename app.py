from flask import Flask, request, jsonify, g, Response
import logging
import time
import uuid

app = Flask(__name__)
logger = logging.getLogger('app')
start_time = time.time()
VERSION = '1.0.0'
BUILD = 'local'

DEPENDENCIES_OK = True

def get_health_metadata():
    uptime = time.time() - start_time
    return {
        'status': 'alive',
        'uptime_seconds': uptime,
        'version': VERSION,
        'build': BUILD
    }

def check_dependencies():
    return DEPENDENCIES_OK

def get_request_id():
    upstream_id = request.headers.get('X-Request-ID')
    if upstream_id:
        return upstream_id
    return str(uuid.uuid4())

@app.before_request
def set_request_id():
    g.request_id = get_request_id()

@app.before_request
def log_request():
    request_id = getattr(g, 'request_id', 'unknown')
    logger.info(f'Request path: {request.path} request_id={request_id}')

@app.after_request
def add_request_id_header(response: Response) -> Response:
    request_id = getattr(g, 'request_id', None)
    if request_id:
        response.headers['X-Request-ID'] = request_id
    return response

@app.route('/health')
def health_check():
    return 'OK', 200

@app.route('/live')
def live_check():
    return jsonify(get_health_metadata()), 200

@app.route('/ready')
def ready_check():
    metadata = get_health_metadata()
    if check_dependencies():
        metadata['status'] = 'ready'
        return jsonify(metadata), 200
    else:
        metadata['status'] = 'not_ready'
        return jsonify(metadata), 503