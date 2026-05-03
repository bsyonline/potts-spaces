import pytest
from app import app


def test_request_logging(caplog):
    with app.test_client() as client:
        with caplog.at_level('INFO'):
            response = client.get('/')
    
    assert '/' in caplog.text
    assert response.status_code == 200


def test_existing_behavior_unchanged():
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
