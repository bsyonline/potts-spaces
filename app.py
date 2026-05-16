import time
import uuid
import threading
import hashlib
import logging
import traceback
import copy
import re
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

MAX_PER_PAGE = 100

_config_manager = None
_config_lock = threading.Lock()

VALID_SORT_FIELDS = ['name', 'id']
VALID_FILTER_FIELDS = ['name', 'id']


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


def parse_filter_value(filter_str, resource):
    if ':' not in filter_str:
        return None, 'Invalid filter syntax'
    parts = filter_str.split(':', 1)
    if len(parts) != 2:
        return None, 'Invalid filter syntax'
    field, value = parts
    if field not in VALID_FILTER_FIELDS and not field.startswith('data.'):
        return None, f'Invalid filter field: {field}'
    actual_value = None
    if field.startswith('data.'):
        data_field = field.split('.', 1)[1]
        if 'data' in resource and isinstance(resource['data'], dict):
            actual_value = resource['data'].get(data_field)
    else:
        actual_value = resource.get(field)
    if actual_value is None:
        return False, None
    if value.endswith('*'):
        prefix = value[:-1]
        return str(actual_value).startswith(prefix), None
    return str(actual_value) == value, None


def parse_sort_value(sort_str):
    if ':' in sort_str:
        parts = sort_str.split(':')
        if len(parts) > 2:
            return None, None, 'Invalid sort format'
        field, direction = parts[0], parts[1]
    else:
        field = sort_str
        direction = 'asc'
    if field not in VALID_SORT_FIELDS and not field.startswith('data.'):
        return None, None, f'Invalid sort field: {field}'
    if direction not in ['asc', 'desc']:
        return None, None, f'Invalid sort direction: {direction}'
    return field, direction, None


def get_sort_key(resource, field):
    if field.startswith('data.'):
        data_field = field.split('.', 1)[1]
        if 'data' in resource and isinstance(resource['data'], dict):
            val = resource['data'].get(data_field)
            if isinstance(val, (int, float)):
                return (0, val)
            return (1, str(val or ''))
        return (1, '')
    val = resource.get(field)
    if isinstance(val, (int, float)):
        return (0, val)
    return (1, str(val or ''))


@app.route('/resources', methods=['GET'])
def list_resources():
    errors = []
    allowed_params = ['page', 'per_page', 'filter', 'sort']
    for param in request.args.keys():
        if param not in allowed_params:
            errors.append({
                'field': param,
                'message': f'Unsupported query parameter: {param}'
            })
    if errors:
        return jsonify({
            'code': 'INVALID_QUERY',
            'message': 'Invalid query parameters',
            'errors': errors,
            'request_id': g.request_id
        }), 400
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', str(MAX_PER_PAGE))
    try:
        page_int = int(page)
        if page_int <= 0:
            errors.append({
                'field': 'page',
                'message': 'Page must be a positive integer',
                'constraint': '> 0',
                'actual': page
            })
    except ValueError:
        errors.append({
            'field': 'page',
            'message': 'Page must be an integer',
            'actual': page
        })
        page_int = 1
    try:
        per_page_int = int(per_page)
        if per_page_int <= 0:
            errors.append({
                'field': 'per_page',
                'message': 'Per_page must be a positive integer',
                'constraint': '> 0',
                'actual': per_page
            })
        if per_page_int > MAX_PER_PAGE:
            errors.append({
                'field': 'per_page',
                'message': f'Per_page exceeds maximum allowed: {MAX_PER_PAGE}',
                'constraint': f'<= {MAX_PER_PAGE}',
                'actual': per_page
            })
    except ValueError:
        errors.append({
            'field': 'per_page',
            'message': 'Per_page must be an integer',
            'actual': per_page
        })
        per_page_int = MAX_PER_PAGE
    filter_strs = request.args.getlist('filter')
    sort_str = request.args.get('sort')
    sort_field = None
    sort_direction = 'asc'
    if sort_str:
        sort_field, sort_direction, sort_error = parse_sort_value(sort_str)
        if sort_error:
            errors.append({
                'field': 'sort',
                'message': sort_error,
                'actual': sort_str
            })
    for filter_str in filter_strs:
        if ':' not in filter_str:
            errors.append({
                'field': 'filter',
                'message': 'Invalid filter syntax',
                'actual': filter_str
            })
        else:
            parts = filter_str.split(':', 1)
            field = parts[0]
            if field not in VALID_FILTER_FIELDS and not field.startswith('data.'):
                errors.append({
                    'field': 'filter',
                    'message': f'Invalid filter field: {field}',
                    'actual': filter_str
                })
    if errors:
        return jsonify({
            'code': 'INVALID_QUERY',
            'message': 'Invalid query parameters',
            'errors': errors,
            'request_id': g.request_id
        }), 400
    with resources_lock:
        resources = list(resources_store.values())
    if filter_strs:
        filtered = []
        for r in resources:
            match = True
            for filter_str in filter_strs:
                result, _ = parse_filter_value(filter_str, r)
                if result is False:
                    match = False
                    break
            if match:
                filtered.append(r)
        resources = filtered
    if sort_field:
        resources.sort(
            key=lambda r: (get_sort_key(r, sort_field), r.get('id', '')),
            reverse=(sort_direction == 'desc')
        )
    else:
        resources.sort(key=lambda r: r.get('id', ''))
    total = len(resources)
    start = (page_int - 1) * per_page_int
    end = start + per_page_int
    items = resources[start:end]
    return jsonify({
        'items': items,
        'total': total,
        'request_id': g.request_id
    }), 200