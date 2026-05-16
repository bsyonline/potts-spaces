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