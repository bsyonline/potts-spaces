from flask import Flask, request, jsonify
import logging
import time

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

@app.before_request
def log_request():
    logger.info(f'Request path: {request.path}')

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