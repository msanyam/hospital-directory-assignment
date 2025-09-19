import pytest
import uuid
from fastapi import status


class TestBatchAPIEndpoints:
    """Test batch-related API endpoints (simplified)."""

    def test_get_hospitals_by_batch_id_success(self, client, create_test_batch, bypass_rate_limit):
        """Test getting hospitals by batch ID."""
        hospitals, batch_id = create_test_batch(3)

        response = client.get(f"/hospitals/batch/{batch_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        assert all(h["creation_batch_id"] == str(batch_id) for h in data)

    def test_get_hospitals_by_batch_id_not_found(self, client, bypass_rate_limit):
        """Test getting hospitals by non-existent batch ID."""
        batch_id = uuid.uuid4()

        response = client.get(f"/hospitals/batch/{batch_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "No hospitals found" in response.json()["detail"]

    def test_delete_hospitals_by_batch_success(self, client, create_test_batch, bypass_rate_limit):
        """Test deleting hospitals by batch ID."""
        hospitals, batch_id = create_test_batch(3)

        response = client.delete(f"/hospitals/batch/{batch_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["deleted_count"] == 3
        assert str(batch_id) in data["message"]

        # Verify they're gone
        response = client.get(f"/hospitals/batch/{batch_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_activate_hospitals_by_batch_success(self, client, create_test_batch, bypass_rate_limit):
        """Test activating hospitals by batch ID."""
        hospitals, batch_id = create_test_batch(3, active=False)

        response = client.patch(f"/hospitals/batch/{batch_id}/activate")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["activated_count"] == 3

        # Verify they're active
        response = client.get(f"/hospitals/batch/{batch_id}")
        hospitals_data = response.json()
        assert all(h["active"] for h in hospitals_data)

    def test_activate_hospitals_with_active_hospital_fails(self, client, create_test_batch, bypass_rate_limit):
        """Test that activation fails if any hospital is already active."""
        hospitals, batch_id = create_test_batch(3, active=False)

        # Manually activate one hospital
        hospitals[0].active = True
        from app import database
        database.update_hospital(hospitals[0].id, hospitals[0])

        response = client.patch(f"/hospitals/batch/{batch_id}/activate")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already active" in response.json()["detail"]

    def test_batch_size_limit_enforcement(self, client, mock_slow_task, bypass_rate_limit):
        """Test batch size limit enforcement."""
        batch_id = str(uuid.uuid4())

        # Create 20 hospitals (should succeed)
        for i in range(20):
            hospital_data = {
                "name": f"Hospital {i+1:02d}",
                "address": f"{i+1}00 Main St",
                "creation_batch_id": batch_id
            }
            response = client.post("/hospitals/", json=hospital_data)
            assert response.status_code == status.HTTP_200_OK

        # Try 21st - should fail
        hospital_data = {
            "name": "Hospital 21",
            "address": "2100 Main St",
            "creation_batch_id": batch_id
        }
        response = client.post("/hospitals/", json=hospital_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Verify still only 20
        response = client.get(f"/hospitals/batch/{batch_id}")
        assert len(response.json()) == 20