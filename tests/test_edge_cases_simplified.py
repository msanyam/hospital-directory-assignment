import pytest
import uuid
from fastapi import status


class TestUUIDValidation:
    """Test UUID validation edge cases."""

    def test_valid_uuid_formats(self, client, mock_slow_task, bypass_rate_limit):
        """Test various valid UUID formats."""
        valid_uuids = [
            str(uuid.uuid4()),  # Standard format
            str(uuid.uuid4()).upper(),  # Uppercase
        ]

        for i, test_uuid in enumerate(valid_uuids):
            hospital_data = {
                "name": f"UUID Test Hospital {i+1}",
                "address": f"{i+1}23 UUID St",
                "creation_batch_id": test_uuid
            }
            response = client.post("/hospitals/", json=hospital_data)
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["creation_batch_id"] == test_uuid.lower()

    def test_invalid_uuid_formats(self, client, bypass_rate_limit):
        """Test invalid UUID formats."""
        invalid_uuids = [
            "not-a-uuid",
            "12345",
            "550e8400-e29b-41d4-a716",  # Too short
            "550e8400-e29b-41d4-a716-44665544000g",  # Invalid character
        ]

        for i, test_uuid in enumerate(invalid_uuids):
            hospital_data = {
                "name": f"Invalid UUID Test {i+1}",
                "address": f"{i+1}23 Invalid St",
                "creation_batch_id": test_uuid
            }
            response = client.post("/hospitals/", json=hospital_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestStringValidation:
    """Test string validation edge cases."""

    def test_empty_required_fields(self, client, bypass_rate_limit):
        """Test empty and whitespace-only strings in required fields."""
        invalid_cases = [
            {"name": "", "address": "123 Valid St"},
            {"name": "   ", "address": "123 Valid St"},
            {"name": "Valid Name", "address": ""},
            {"name": "Valid Name", "address": "   "},
        ]

        for hospital_data in invalid_cases:
            response = client.post("/hospitals/", json=hospital_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_special_characters_in_strings(self, client, mock_slow_task, bypass_rate_limit):
        """Test special characters in string fields."""
        special_cases = [
            {
                "name": "Hospital & Clinic",
                "address": "123 Main St. #456",
                "phone": "+1-555-123-4567"
            },
            {
                "name": "St. Mary's Hospital",
                "address": "789 O'Brien Ave",
                "phone": "(555) 987-6543"
            },
            {
                "name": 'Hospital "Quotes"',
                "address": "123 'Apostrophe' St",
                "phone": "555-123-4567 ext. 123"
            }
        ]

        for hospital_data in special_cases:
            response = client.post("/hospitals/", json=hospital_data)
            assert response.status_code == status.HTTP_200_OK

            data = response.json()
            assert data["name"] == hospital_data["name"]
            assert data["address"] == hospital_data["address"]
            assert data["phone"] == hospital_data["phone"]


class TestMissingFields:
    """Test missing and null field handling."""

    def test_missing_required_fields(self, client, bypass_rate_limit):
        """Test requests with missing required fields."""
        invalid_cases = [
            {"address": "123 Main St"},  # Missing name
            {"name": "Test Hospital"},   # Missing address
            {"phone": "555-1234"},       # Missing both name and address
            {},                          # Empty object
        ]

        for hospital_data in invalid_cases:
            response = client.post("/hospitals/", json=hospital_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_null_optional_fields(self, client, mock_slow_task, bypass_rate_limit):
        """Test null values in optional fields."""
        hospital_data = {
            "name": "Test Hospital",
            "address": "123 Main St",
            "phone": None,
            "creation_batch_id": None
        }

        response = client.post("/hospitals/", json=hospital_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["phone"] is None
        assert data["creation_batch_id"] is None


class TestBoundaryValues:
    """Test boundary value conditions."""

    def test_integer_boundaries(self, client, bypass_rate_limit):
        """Test integer boundary values for hospital IDs."""
        # Test with very large hospital ID (should not exist)
        response = client.get("/hospitals/999999999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Test with zero (should not exist)
        response = client.get("/hospitals/0")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Test with negative ID (also returns not found)
        response = client.get("/hospitals/-1")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_fifo_storage_boundary(self, reset_database):
        """Test FIFO storage boundary conditions using database directly."""
        from app import database
        from app.models import Hospital
        from collections import deque

        # Save original database
        original_db = database.hospitals_db
        original_next_id = database.next_id

        try:
            # Set very small limit for testing
            database.hospitals_db = deque(maxlen=3)
            database.next_id = 1

            created_ids = []

            # Create exactly at limit using database directly
            for i in range(3):
                hospital = Hospital(
                    id=0,  # Will be set by create_hospital
                    name=f"FIFO Test {i+1}",
                    address=f"{i+1}00 FIFO St",
                    active=True
                )
                created = database.create_hospital(hospital)
                created_ids.append(created.id)

            assert len(database.hospitals_db) == 3

            # Add one more (should evict first)
            hospital = Hospital(
                id=0,
                name="FIFO Test 4",
                address="400 FIFO St",
                active=True
            )
            fourth = database.create_hospital(hospital)

            # Should still have only 3 hospitals
            assert len(database.hospitals_db) == 3

            # First should be gone, others should exist
            assert database.get_hospital_by_id(created_ids[0]) is None
            assert database.get_hospital_by_id(created_ids[1]) is not None
            assert database.get_hospital_by_id(created_ids[2]) is not None
            assert database.get_hospital_by_id(fourth.id) is not None

        finally:
            # Restore original database
            database.hospitals_db = original_db
            database.next_id = original_next_id