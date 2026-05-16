import pytest
from app import app


@pytest.fixture
def client():
    app.testing = True
    return app.test_client()


def test_health_endpoint_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200