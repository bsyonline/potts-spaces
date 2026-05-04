import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_request_path_is_logged(client, capsys):
    response = client.get("/health")
    captured = capsys.readouterr()
    assert "/health" in captured.out
