import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import uuid
from collections import deque

# Import the application
from app.main import app
from app import database
from app.models import Hospital
from app.config import MAX_TOTAL_HOSPITALS

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture(autouse=True)
def reset_database():
    """Reset the database before each test."""
    database.hospitals_db = deque(maxlen=MAX_TOTAL_HOSPITALS)
    database.next_id = 1
    yield
    # Cleanup after test
    database.hospitals_db = deque(maxlen=MAX_TOTAL_HOSPITALS)
    database.next_id = 1

@pytest.fixture
def mock_slow_task():
    """Mock the slow running task to speed up tests."""
    with patch('app.main.slow_running_task', return_value=None):
        yield

@pytest.fixture
def sample_hospital_data():
    """Sample hospital data for testing."""
    return {
        "name": "Test Hospital",
        "address": "123 Test St",
        "phone": "555-0123"
    }

@pytest.fixture
def sample_batch_id():
    """Sample batch ID for testing."""
    return str(uuid.uuid4())

@pytest.fixture
def create_test_hospital():
    """Factory function to create test hospitals."""
    def _create_hospital(name="Test Hospital", address="123 Test St", phone="555-0123", batch_id=None, active=True):
        hospital = Hospital(
            id=database.next_id,
            name=name,
            address=address,
            phone=phone,
            creation_batch_id=batch_id,
            active=active
        )
        database.next_id += 1
        database.hospitals_db.append(hospital)
        return hospital
    return _create_hospital

@pytest.fixture
def create_test_batch():
    """Factory function to create a batch of test hospitals."""
    def _create_batch(count=5, batch_id=None, active=False):
        if batch_id is None:
            batch_id = uuid.uuid4()

        hospitals = []
        for i in range(count):
            hospital = Hospital(
                id=database.next_id,
                name=f"Hospital {i+1}",
                address=f"{i+1}23 Test St",
                phone=f"555-{i:04d}",
                creation_batch_id=batch_id,
                active=active
            )
            database.next_id += 1
            database.hospitals_db.append(hospital)
            hospitals.append(hospital)

        return hospitals, batch_id
    return _create_batch

@pytest.fixture
def create_test_hospital_direct():
    """Factory function to create test hospitals directly in database."""
    def _create_hospital_direct(name="Test Hospital", address="123 Test St", phone="555-0123", batch_id=None, active=True):
        hospital = Hospital(
            id=database.next_id,
            name=name,
            address=address,
            phone=phone,
            creation_batch_id=batch_id,
            active=active
        )
        created = database.create_hospital(hospital)
        return created
    return _create_hospital_direct

@pytest.fixture
def bypass_rate_limit():
    """Bypass rate limiting for testing."""
    with patch('slowapi.Limiter.limit', lambda self, rate: lambda func: func):
        yield