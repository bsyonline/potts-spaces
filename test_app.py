import pytest
from io import StringIO
import sys
from app import app


def test_request_logging():
    captured_output = StringIO()
    sys.stdout = captured_output
    
    with app.test_client() as client:
        response = client.get('/test-path')
    
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    
    assert '/test-path' in output
    assert response.status_code == 200


def test_existing_behavior_unchanged():
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200