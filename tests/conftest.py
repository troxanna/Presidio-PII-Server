import pytest
from fastapi.testclient import TestClient
from app.interface.api import app

@pytest.fixture(scope="session")
def client():
    return TestClient(app)