from fastapi.testclient import TestClient

from main import app


def test_hello_endpoint_returns_200():
    client = TestClient(app)
    response = client.get("/hello")
    assert response.status_code == 200


def test_hello_endpoint_returns_message():
    client = TestClient(app)
    response = client.get("/hello")
    assert "message" in response.json()


def test_health_endpoint_returns_200():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_returns_healthy_status():
    client = TestClient(app)
    response = client.get("/health")
    assert response.json()["status"] == "healthy"