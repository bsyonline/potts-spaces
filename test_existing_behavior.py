import pytest
from app import app

def test_existing_behavior_unchanged():
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200
        assert 'Hello, World!' in response.data.decode()