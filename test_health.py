import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint_returns_200(client):
    """Test that /health endpoint returns HTTP 200 with proper JSON response."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {'status': 'ok'}
    assert response.content_type == 'application/json'