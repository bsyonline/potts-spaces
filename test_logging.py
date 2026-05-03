import pytest
from app import app

def test_request_path_logging(capsys):
    with app.test_client() as client:
        client.get('/test-path')
    
    captured = capsys.readouterr()
    assert '/test-path' in captured.out, f"Expected '/test-path' in logs, got: {captured.out}"

def test_request_path_logging_different_paths(capsys):
    with app.test_client() as client:
        client.get('/api/users')
        client.get('/health')
    
    captured = capsys.readouterr()
    assert '/api/users' in captured.out, f"Expected '/api/users' in logs"
    assert '/health' in captured.out, f"Expected '/health' in logs"
