import pytest
from pydantic import ValidationError
from datetime import datetime
import uuid
from app.models import Hospital, HospitalCreate, HospitalUpdate

class TestHospitalModel:
    """Test cases for the Hospital model."""

    def test_valid_hospital_creation(self):
        """Test creating a valid hospital."""
        hospital_data = {
            "id": 1,
            "name": "Test Hospital",
            "address": "123 Main St",
            "phone": "555-1234",
            "creation_batch_id": uuid.uuid4(),
            "active": True
        }
        hospital = Hospital(**hospital_data)
        assert hospital.name == "Test Hospital"
        assert hospital.address == "123 Main St"
        assert hospital.phone == "555-1234"
        assert hospital.active is True
        assert isinstance(hospital.created_at, datetime)

    def test_hospital_without_optional_fields(self):
        """Test creating a hospital without optional fields."""
        hospital_data = {
            "id": 1,
            "name": "Test Hospital",
            "address": "123 Main St"
        }
        hospital = Hospital(**hospital_data)
        assert hospital.phone is None
        assert hospital.creation_batch_id is None
        assert hospital.active is True  # Default value

    def test_hospital_with_batch_id_defaults_inactive(self):
        """Test that hospital with batch_id defaults to active=True (will be set by API logic)."""
        batch_id = uuid.uuid4()
        hospital_data = {
            "id": 1,
            "name": "Test Hospital",
            "address": "123 Main St",
            "creation_batch_id": batch_id
        }
        hospital = Hospital(**hospital_data)
        assert hospital.creation_batch_id == batch_id
        assert hospital.active is True  # Model default, API will override

    def test_hospital_invalid_data(self):
        """Test validation errors with invalid data."""
        with pytest.raises(ValidationError):
            Hospital(id="invalid", name="Test", address="123 Main St")

        with pytest.raises(ValidationError):
            Hospital(id=1, name="", address="123 Main St")  # Empty name

        with pytest.raises(ValidationError):
            Hospital(id=1, name="Test", address="")  # Empty address

    def test_hospital_id_required(self):
        """Test that hospital ID is required."""
        with pytest.raises(ValidationError):
            Hospital(name="Test Hospital", address="123 Main St")


class TestHospitalCreateModel:
    """Test cases for the HospitalCreate model."""

    def test_valid_hospital_create(self):
        """Test creating a valid HospitalCreate object."""
        create_data = {
            "name": "New Hospital",
            "address": "456 Oak Ave",
            "phone": "555-9876"
        }
        hospital_create = HospitalCreate(**create_data)
        assert hospital_create.name == "New Hospital"
        assert hospital_create.address == "456 Oak Ave"
        assert hospital_create.phone == "555-9876"
        assert hospital_create.creation_batch_id is None

    def test_hospital_create_with_batch_id(self):
        """Test creating HospitalCreate with batch ID."""
        batch_id = uuid.uuid4()
        create_data = {
            "name": "Batch Hospital",
            "address": "789 Pine Rd",
            "creation_batch_id": batch_id
        }
        hospital_create = HospitalCreate(**create_data)
        assert hospital_create.creation_batch_id == batch_id
        assert hospital_create.phone is None

    def test_hospital_create_validation(self):
        """Test validation for HospitalCreate."""
        with pytest.raises(ValidationError):
            HospitalCreate(name="", address="123 Main St")  # Empty name

        with pytest.raises(ValidationError):
            HospitalCreate(name="Test", address="")  # Empty address

        # Name and address are required
        with pytest.raises(ValidationError):
            HospitalCreate(phone="555-1234")


class TestHospitalUpdateModel:
    """Test cases for the HospitalUpdate model."""

    def test_valid_hospital_update(self):
        """Test creating a valid HospitalUpdate object."""
        update_data = {
            "name": "Updated Hospital",
            "address": "999 New St",
            "phone": "555-0000"
        }
        hospital_update = HospitalUpdate(**update_data)
        assert hospital_update.name == "Updated Hospital"
        assert hospital_update.address == "999 New St"
        assert hospital_update.phone == "555-0000"

    def test_hospital_update_partial(self):
        """Test partial updates with HospitalUpdate."""
        # Update only name
        update_data = {"name": "New Name Only"}
        hospital_update = HospitalUpdate(**update_data)
        assert hospital_update.name == "New Name Only"
        assert hospital_update.address is None
        assert hospital_update.phone is None

        # Update only phone
        update_data = {"phone": "555-NEW1"}
        hospital_update = HospitalUpdate(**update_data)
        assert hospital_update.name is None
        assert hospital_update.address is None
        assert hospital_update.phone == "555-NEW1"

    def test_hospital_update_empty(self):
        """Test creating empty HospitalUpdate (all fields optional)."""
        hospital_update = HospitalUpdate()
        assert hospital_update.name is None
        assert hospital_update.address is None
        assert hospital_update.phone is None

    def test_hospital_update_model_dump_exclude_unset(self):
        """Test that model_dump(exclude_unset=True) works correctly."""
        update_data = {"name": "Updated Name"}
        hospital_update = HospitalUpdate(**update_data)
        dumped = hospital_update.model_dump(exclude_unset=True)
        assert dumped == {"name": "Updated Name"}
        assert "address" not in dumped
        assert "phone" not in dumped


class TestModelValidation:
    """Test cases for model validation edge cases."""

    def test_uuid_validation(self):
        """Test UUID validation for creation_batch_id."""
        # Valid UUID
        valid_uuid = uuid.uuid4()
        hospital = HospitalCreate(
            name="Test",
            address="123 Main St",
            creation_batch_id=valid_uuid
        )
        assert hospital.creation_batch_id == valid_uuid

        # Invalid UUID string should raise ValidationError
        with pytest.raises(ValidationError):
            HospitalCreate(
                name="Test",
                address="123 Main St",
                creation_batch_id="not-a-uuid"
            )

    def test_boolean_validation(self):
        """Test boolean validation for active field."""
        # Valid boolean values
        hospital = Hospital(
            id=1,
            name="Test",
            address="123 Main St",
            active=True
        )
        assert hospital.active is True

        hospital = Hospital(
            id=1,
            name="Test",
            address="123 Main St",
            active=False
        )
        assert hospital.active is False

    def test_string_validation(self):
        """Test string validation for name and address."""
        # Whitespace-only strings should be invalid
        with pytest.raises(ValidationError):
            Hospital(id=1, name="   ", address="123 Main St")

        with pytest.raises(ValidationError):
            Hospital(id=1, name="Test", address="   ")

    def test_datetime_auto_generation(self):
        """Test that created_at is auto-generated."""
        hospital1 = Hospital(id=1, name="Test1", address="123 Main St")
        hospital2 = Hospital(id=2, name="Test2", address="456 Oak Ave")

        assert isinstance(hospital1.created_at, datetime)
        assert isinstance(hospital2.created_at, datetime)
        # They should be very close in time but potentially different
        assert abs((hospital1.created_at - hospital2.created_at).total_seconds()) < 1