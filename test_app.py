import pytest
from app import app


@pytest.fixture
def client():
    app.testing = True
    return app.test_client()


def test_health_endpoint_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_request_path_is_logged_to_stdout(client, capfd):
    client.get("/test-path")
    captured = capfd.readouterr()
    assert "/test-path" in captured.out