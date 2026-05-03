import pytest
from io import StringIO
import sys
from app import app

def test_request_path_logging():
    captured_output = StringIO()
    sys.stdout = captured_output
    
    with app.test_client() as client:
        response = client.get('/test-path')
    
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    
    assert '/test-path' in output, f"Expected '/test-path' in logs, got: {output}"

def test_request_path_logging_different_paths():
    captured_output = StringIO()
    sys.stdout = captured_output
    
    with app.test_client() as client:
        response1 = client.get('/api/users')
        response2 = client.get('/health')
    
    sys.stdout = sys.__stdout__
    output = captured_output.getvalue()
    
    assert '/api/users' in output, f"Expected '/api/users' in logs"
    assert '/health' in output, f"Expected '/health' in logs"