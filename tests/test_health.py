import pytest
import logging
from io import StringIO
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_check_returns_200(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.data == b'OK'


def test_request_logging_logs_incoming_path(client):
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.INFO)
    logger = logging.getLogger('app')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    response = client.get('/health')
    
    log_contents = log_stream.getvalue()
    assert '/health' in log_contents
    assert 'Request' in log_contents or 'request' in log_contents


def test_live_endpoint_returns_json_with_required_fields(client):
    response = client.get('/live')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert 'uptime_seconds' in data
    assert 'version' in data
    assert 'build' in data


def test_live_endpoint_field_types(client):
    response = client.get('/live')
    data = response.get_json()
    assert isinstance(data['status'], str)
    assert isinstance(data['uptime_seconds'], (int, float))
    assert isinstance(data['version'], str)
    assert isinstance(data['build'], str)


def test_live_endpoint_status_is_alive(client):
    response = client.get('/live')
    data = response.get_json()
    assert data['status'] == 'alive'


def test_live_endpoint_uptime_is_positive(client):
    response = client.get('/live')
    data = response.get_json()
    assert data['uptime_seconds'] >= 0


def test_ready_endpoint_returns_json_with_required_fields(client):
    response = client.get('/ready')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert 'uptime_seconds' in data
    assert 'version' in data
    assert 'build' in data


def test_ready_endpoint_field_types(client):
    response = client.get('/ready')
    data = response.get_json()
    assert isinstance(data['status'], str)
    assert isinstance(data['uptime_seconds'], (int, float))
    assert isinstance(data['version'], str)
    assert isinstance(data['build'], str)


def test_ready_endpoint_status_when_dependencies_ok(client):
    response = client.get('/ready')
    data = response.get_json()
    assert data['status'] in ['ready', 'not_ready']


def test_ready_endpoint_returns_not_ready_when_dependencies_fail(client):
    import app as app_module
    original_deps_ok = app_module.DEPENDENCIES_OK
    app_module.DEPENDENCIES_OK = False
    
    response = client.get('/ready')
    
    app_module.DEPENDENCIES_OK = original_deps_ok
    
    assert response.status_code == 503
    data = response.get_json()
    assert data['status'] == 'not_ready'


def test_health_endpoint_remains_compatible(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.data == b'OK'