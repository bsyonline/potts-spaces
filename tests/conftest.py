import pytest
from fastapi.testclient import TestClient

from potts_spaces.app import app


@pytest.fixture
def client():
    return TestClient(app)