import pytest
import sys
from io import StringIO
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_request_path_is_logged(client):
    captured_output = StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured_output
    
    client.get('/health')
    
    sys.stdout = old_stdout
    logged_output = captured_output.getvalue()
    
    assert '/health' in logged_output