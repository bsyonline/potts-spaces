import time
import uuid
import threading
import hashlib
import logging
import traceback
import copy
from flask import Flask, request, jsonify, g

app = Flask(__name__)
START_TIME = time.time()
VERSION = '1.0.0'
BUILD = 'development'

logger = logging.getLogger(__name__)

idempotency_store = {}
idempotency_lock = threading.Lock()
resources_store = {}
resources_lock = threading.Lock()

DEFAULT_CONFIG = {
    'max_requests_per_second': 50,
    'timeout_seconds': 10,
    'feature_flags': {}
}

_config_manager = None
_config_lock = threading.Lock()


class ConfigManager:
    def __init__(self, initial_config=None):
        self._config = initial_config or copy.deepcopy(DEFAULT_CONFIG)
        self._lock = threading.RLock()
        
    def get_config(self):
        with self._lock:
            return copy.deepcopy(self._config)
            
    def reload_config(self, new_config):
        errors = validate_config(new_config)
        if errors:
            return False, errors
        with self._lock:
            self._config = copy.deepcopy(new_config)
        return True, None
        
    def rollback(self, old_config):
        with self._lock:
            self._config = copy.deepcopy(old_config)


def get_config_manager():
    global _config_manager
    if _config_manager is None:
        with _config_lock:
            if _config_manager is None:
                _config_manager = ConfigManager()
    return _config_manager


def validate_config(config):
    errors = []
    if 'max_requests_per_second' in config:
        value = config['max_requests_per_second']
        if not isinstance(value, int) or value < 0:
            errors.append({
                'field': 'max_requests_per_second',
                'message': 'must be a non-negative integer',
                'constraint': '>= 0',
                'actual': value
            })
    if 'timeout_seconds' in config:
        value = config['timeout_seconds']
        if not isinstance(value, int) or value <= 0:
            errors.append({
                'field': 'timeout_seconds',
                'message': 'must be a positive integer',
                'constraint': '> 0',
                'actual': value
            })
    return errors


def get_config():
    return get_config_manager().get_config()


def reload_config(new_config):
    return get_config_manager().reload_config(new_config)


def make_error_response(code, message, status_code):
    error_data = {
        'code': code,
        'message': message,
        'request_id': g.request_id
    }
    return jsonify(error_data), status_code


@app.before_request
def handle_request_tracing():
    request_id = request.headers.get('X-Request-ID')
    if not request_id:
        request_id = str(uuid.uuid4())
    g.request_id = request_id
    print(f'{g.request_id} {request.path}')


@app.after_request
def add_request_id_header(response):
    response.headers['X-Request-ID'] = g.request_id
    return response


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


def compute_payload_hash(payload):
    if payload is None:
        return ''
    return hashlib.sha256(str(payload).encode()).hexdigest()


@app.route('/resources', methods=['POST'])
def create_resource():
    data = request.get_json() or {}
    idempotency_key = request.headers.get('X-Idempotency-Key')
    
    if not idempotency_key:
        resource_id = str(uuid.uuid4())
        with resources_lock:
            resources_store[resource_id] = {
                'id': resource_id,
                'name': data.get('name'),
                'data': data.get('data')
            }
        return jsonify({'id': resource_id, 'name': data.get('name'), 'data': data.get('data')}), 201
    
    payload_hash = compute_payload_hash(data)
    
    with idempotency_lock:
        existing = idempotency_store.get(idempotency_key)
        
        if existing:
            if existing['payload_hash'] == payload_hash:
                return jsonify(existing['response']), 201
            else:
                return make_error_response(
                    'IDEMPOTENCY_CONFLICT',
                    'Idempotency conflict: same key with different payload',
                    409
                )
        
        resource_id = str(uuid.uuid4())
        response_data = {
            'id': resource_id,
            'name': data.get('name'),
            'data': data.get('data')
        }
        
        idempotency_store[idempotency_key] = {
            'payload_hash': payload_hash,
            'response': response_data,
            'resource_id': resource_id
        }
        
        with resources_lock:
            resources_store[resource_id] = response_data
    
    return jsonify(response_data), 201


@app.route('/admin/config', methods=['GET'])
def get_current_config():
    current = get_config()
    return jsonify({'config': current}), 200


@app.route('/admin/config/reload', methods=['POST'])
def handle_config_reload():
    data = request.get_json() or {}
    new_config = data.get('config', {})
    success, errors = reload_config(new_config)
    if success:
        return jsonify({'status': 'success', 'config': get_config()}), 200
    return jsonify({
        'code': 'CONFIG_VALIDATION_ERROR',
        'message': 'Config validation failed',
        'errors': errors,
        'request_id': g.request_id
    }), 400


@app.errorhandler(404)
def handle_not_found(error):
    return make_error_response('NOT_FOUND', 'Resource not found', 404)


@app.errorhandler(400)
def handle_bad_request(error):
    logger.error(f'Bad request error: {error}\n{traceback.format_exc()}')
    return make_error_response('BAD_REQUEST', 'Invalid request payload', 400)