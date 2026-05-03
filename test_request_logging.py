import io
import sys
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_request_logging_logs_path(capfd):
    """Test that incoming request paths are logged to stdout."""
    with app.test_client() as client:
        response = client.get('/test-path')
        
        captured = capfd.readouterr()
        assert '/test-path' in captured.out


def test_request_logging_preserves_response():
    """Test that existing behavior (response) remains unchanged."""
    with app.test_client() as client:
        response = client.get('/another-path')
        assert response.status_code == 404