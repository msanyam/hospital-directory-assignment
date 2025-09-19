from fastapi import status


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "OK"}


class TestHospitalCRUD:
    """Test hospital CRUD operations via API."""

    def test_create_hospital_success(
        self, client, mock_slow_task, sample_hospital_data
    ):
        """Test successful hospital creation."""
        response = client.post("/hospitals/", json=sample_hospital_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == sample_hospital_data["name"]
        assert data["address"] == sample_hospital_data["address"]
        assert data["phone"] == sample_hospital_data["phone"]
        assert data["active"] is True
        assert data["creation_batch_id"] is None
        assert "created_at" in data

    def test_create_hospital_with_batch_id(
        self,
        client,
        mock_slow_task,
        sample_hospital_data,
        sample_batch_id,
    ):
        """Test creating hospital with batch ID."""
        sample_hospital_data["creation_batch_id"] = sample_batch_id

        response = client.post("/hospitals/", json=sample_hospital_data)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["creation_batch_id"] == sample_batch_id
        assert data["active"] is False  # Should be inactive when created with batch ID

    def test_create_hospital_validation_error(self, client, bypass_rate_limit):
        """Test validation errors during creation."""
        # Missing required fields
        response = client.post("/hospitals/", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Empty name
        response = client.post(
            "/hospitals/", json={"name": "", "address": "123 Main St"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Empty address
        response = client.post("/hospitals/", json={"name": "Test", "address": ""})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_all_hospitals_empty(self, client):
        """Test getting all hospitals when database is empty."""
        response = client.get("/hospitals/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_all_hospitals_with_data(
        self, client, create_test_hospital
    ):
        """Test getting all hospitals with data."""
        # Create test hospitals
        create_test_hospital("Hospital 1", "123 Main St")
        create_test_hospital("Hospital 2", "456 Oak Ave")

        response = client.get("/hospitals/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        names = [h["name"] for h in data]
        assert "Hospital 1" in names
        assert "Hospital 2" in names

    def test_get_hospital_by_id_success(
        self, client, create_test_hospital
    ):
        """Test getting hospital by ID."""
        hospital = create_test_hospital("Test Hospital")

        response = client.get(f"/hospitals/{hospital.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == hospital.id
        assert data["name"] == "Test Hospital"

    def test_get_hospital_by_id_not_found(self, client):
        """Test getting non-existent hospital."""
        response = client.get("/hospitals/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Hospital not found" in response.json()["detail"]

    def test_update_hospital_success(
        self, client, create_test_hospital
    ):
        """Test updating a hospital."""
        hospital = create_test_hospital("Original Name", "Original Address")

        update_data = {"name": "Updated Name", "phone": "555-9999"}

        response = client.put(f"/hospitals/{hospital.id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["phone"] == "555-9999"
        assert data["address"] == "Original Address"  # Should remain unchanged

    def test_update_hospital_not_found(self, client):
        """Test updating non-existent hospital."""
        update_data = {"name": "New Name"}

        response = client.put("/hospitals/999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_hospital_success(
        self, client, create_test_hospital
    ):
        """Test deleting a hospital."""
        hospital = create_test_hospital("To Delete")

        response = client.delete(f"/hospitals/{hospital.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's gone
        response = client.get(f"/hospitals/{hospital.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_hospital_not_found(self, client):
        """Test deleting non-existent hospital."""
        response = client.delete("/hospitals/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND




class TestAPIValidation:
    """Test API validation and error handling."""

    def test_invalid_uuid_format(self, client):
        """Test invalid UUID format in batch operations."""
        invalid_uuid = "not-a-uuid"

        response = client.get(f"/hospitals/batch/{invalid_uuid}")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        response = client.delete(f"/hospitals/batch/{invalid_uuid}")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        response = client.patch(f"/hospitals/batch/{invalid_uuid}/activate")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_hospital_id_format(self, client):
        """Test invalid hospital ID format."""
        response = client.get("/hospitals/not-a-number")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        response = client.put("/hospitals/not-a-number", json={"name": "Test"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        response = client.delete("/hospitals/not-a-number")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_invalid_json_request_body(self, client):
        """Test invalid JSON in request body."""
        # Send malformed JSON
        response = client.post(
            "/hospitals/",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_content_type(self, client):
        """Test request without proper content type."""
        response = client.post("/hospitals/", data='{"name": "Test"}')
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestResponseFormat:
    """Test API response format consistency."""

    def test_hospital_response_format(
        self, client, mock_slow_task, sample_hospital_data
    ):
        """Test that hospital responses have consistent format."""
        response = client.post("/hospitals/", json=sample_hospital_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        required_fields = [
            "id",
            "name",
            "address",
            "phone",
            "creation_batch_id",
            "active",
            "created_at",
        ]
        for field in required_fields:
            assert field in data

        # Check data types
        assert isinstance(data["id"], int)
        assert isinstance(data["name"], str)
        assert isinstance(data["address"], str)
        assert isinstance(data["active"], bool)
        assert isinstance(data["created_at"], str)  # ISO format string

    def test_batch_operation_response_format(
        self, client, create_test_batch
    ):
        """Test batch operation response formats."""
        hospitals, batch_id = create_test_batch(2)

        # Test delete response format
        response = client.delete(f"/hospitals/batch/{batch_id}")
        data = response.json()
        assert "deleted_count" in data
        assert "message" in data
        assert isinstance(data["deleted_count"], int)
        assert isinstance(data["message"], str)

    def test_error_response_format(self, client):
        """Test error response format consistency."""
        response = client.get("/hospitals/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
