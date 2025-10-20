import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from main import app
from database.engine_db import get_db


def override_get_db():
    """Override database dependency for testing with a mock"""
    return MagicMock()


@pytest.fixture(scope="function")
def client():
    """Create test client with overridden database dependency"""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()