import pytest
import time
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestLiveEndpoint:
    def test_live_returns_200(self, client):
        response = client.get('/live')
        assert response.status_code == 200

    def test_live_returns_json(self, client):
        response = client.get('/live')
        assert response.content_type == 'application/json'

    def test_live_has_required_fields(self, client):
        response = client.get('/live')
        data = response.get_json()
        assert 'status' in data
        assert 'uptime_seconds' in data
        assert 'version' in data
        assert 'build' in data

    def test_live_status_is_ok(self, client):
        response = client.get('/live')
        data = response.get_json()
        assert data['status'] == 'ok'

    def test_live_uptime_seconds_is_numeric(self, client):
        response = client.get('/live')
        data = response.get_json()
        assert isinstance(data['uptime_seconds'], (int, float))
        assert data['uptime_seconds'] >= 0

    def test_live_uptime_seconds_is_approximate(self, client):
        response1 = client.get('/live')
        uptime1 = response1.get_json()['uptime_seconds']
        time.sleep(0.1)
        response2 = client.get('/live')
        uptime2 = response2.get_json()['uptime_seconds']
        delta = uptime2 - uptime1
        assert delta >= 0.1
        assert delta < 0.2


class TestReadyEndpoint:
    def test_ready_returns_200_when_healthy(self, client):
        response = client.get('/ready')
        assert response.status_code == 200

    def test_ready_returns_json(self, client):
        response = client.get('/ready')
        assert response.content_type == 'application/json'

    def test_ready_has_required_fields(self, client):
        response = client.get('/ready')
        data = response.get_json()
        assert 'status' in data
        assert 'uptime_seconds' in data
        assert 'version' in data
        assert 'build' in data

    def test_ready_status_is_ok_when_healthy(self, client):
        response = client.get('/ready')
        data = response.get_json()
        assert data['status'] == 'ok'

    def test_ready_uptime_seconds_is_numeric(self, client):
        response = client.get('/ready')
        data = response.get_json()
        assert isinstance(data['uptime_seconds'], (int, float))
        assert data['uptime_seconds'] >= 0

    def test_ready_validates_dependencies(self, client):
        response = client.get('/ready')
        data = response.get_json()
        assert 'dependencies' in data
        assert isinstance(data['dependencies'], dict)


class TestBackwardCompatibility:
    def test_health_endpoint_still_works(self, client):
        response = client.get('/health')
        assert response.status_code == 200

    def test_health_endpoint_returns_ok(self, client):
        response = client.get('/health')
        assert response.data.decode() == 'OK'