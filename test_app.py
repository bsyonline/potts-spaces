import pytest
from app import app

def test_health_check_returns_200():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200