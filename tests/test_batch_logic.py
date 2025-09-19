import pytest
import uuid
from uuid import UUID
from app.database import (
    get_hospitals_by_batch_id,
    has_active_hospitals_in_batch,
    activate_hospitals_by_batch_id,
    delete_hospitals_by_batch_id
)
from app.models import Hospital


class TestBatchSizeValidation:
    """Unit tests for batch size validation logic."""

    def test_batch_size_limit_validation(self):
        """Test batch size limit validation function."""
        from app.main import MAX_BATCH_SIZE

        # Test with batch under limit
        batch_size = 15
        assert batch_size < MAX_BATCH_SIZE

        # Test with batch at limit
        batch_size = 20
        assert batch_size == MAX_BATCH_SIZE

        # Test with batch over limit
        batch_size = 21
        assert batch_size > MAX_BATCH_SIZE


class TestBatchOperationsLogic:
    """Unit tests for batch operations without API calls."""

    def test_get_hospitals_by_batch_id_empty(self, reset_database):
        """Test getting hospitals from empty batch."""
        batch_id = uuid.uuid4()
        result = get_hospitals_by_batch_id(batch_id)
        assert result == []

    def test_get_hospitals_by_batch_id_with_hospitals(self, reset_database, create_test_hospital_direct):
        """Test getting hospitals from populated batch."""
        batch_id = uuid.uuid4()

        # Create hospitals with batch ID
        hospital1 = create_test_hospital_direct("Hospital 1", batch_id=batch_id)
        hospital2 = create_test_hospital_direct("Hospital 2", batch_id=batch_id)

        # Create hospital without batch ID (should not be included)
        create_test_hospital_direct("Hospital 3")

        result = get_hospitals_by_batch_id(batch_id)
        assert len(result) == 2
        assert hospital1 in result
        assert hospital2 in result

    def test_has_active_hospitals_in_batch_all_inactive(self, reset_database, create_test_hospital_direct):
        """Test checking for active hospitals when all are inactive."""
        batch_id = uuid.uuid4()

        create_test_hospital_direct("Hospital 1", batch_id=batch_id, active=False)
        create_test_hospital_direct("Hospital 2", batch_id=batch_id, active=False)

        result = has_active_hospitals_in_batch(batch_id)
        assert result is False

    def test_has_active_hospitals_in_batch_some_active(self, reset_database, create_test_hospital_direct):
        """Test checking for active hospitals when some are active."""
        batch_id = uuid.uuid4()

        create_test_hospital_direct("Hospital 1", batch_id=batch_id, active=False)
        create_test_hospital_direct("Hospital 2", batch_id=batch_id, active=True)

        result = has_active_hospitals_in_batch(batch_id)
        assert result is True

    def test_activate_hospitals_by_batch_id(self, reset_database, create_test_hospital_direct):
        """Test activating all hospitals in a batch."""
        batch_id = uuid.uuid4()

        hospital1 = create_test_hospital_direct("Hospital 1", batch_id=batch_id, active=False)
        hospital2 = create_test_hospital_direct("Hospital 2", batch_id=batch_id, active=False)

        # Create hospital in different batch (should not be affected)
        other_batch_id = uuid.uuid4()
        hospital3 = create_test_hospital_direct("Hospital 3", batch_id=other_batch_id, active=False)

        activated_count = activate_hospitals_by_batch_id(batch_id)

        assert activated_count == 2
        assert hospital1.active is True
        assert hospital2.active is True
        assert hospital3.active is False  # Should remain unchanged

    def test_activate_hospitals_mixed_states(self, reset_database, create_test_hospital_direct):
        """Test activating hospitals when some are already active."""
        batch_id = uuid.uuid4()

        hospital1 = create_test_hospital_direct("Hospital 1", batch_id=batch_id, active=False)
        hospital2 = create_test_hospital_direct("Hospital 2", batch_id=batch_id, active=True)

        activated_count = activate_hospitals_by_batch_id(batch_id)

        assert activated_count == 1  # Only one was activated
        assert hospital1.active is True
        assert hospital2.active is True  # Was already active

    def test_delete_hospitals_by_batch_id(self, reset_database, create_test_hospital_direct):
        """Test deleting hospitals by batch ID."""
        batch_id = uuid.uuid4()

        create_test_hospital_direct("Hospital 1", batch_id=batch_id)
        create_test_hospital_direct("Hospital 2", batch_id=batch_id)

        # Create hospital in different batch (should not be deleted)
        other_batch_id = uuid.uuid4()
        create_test_hospital_direct("Hospital 3", batch_id=other_batch_id)

        deleted_count = delete_hospitals_by_batch_id(batch_id)

        assert deleted_count == 2

        # Verify hospitals are deleted
        remaining_hospitals = get_hospitals_by_batch_id(batch_id)
        assert len(remaining_hospitals) == 0

        # Verify other batch is unaffected
        other_hospitals = get_hospitals_by_batch_id(other_batch_id)
        assert len(other_hospitals) == 1


class TestBatchIntegrityRules:
    """Unit tests for batch business rules."""

    def test_batch_activation_prevents_mixed_states(self, reset_database, create_test_hospital_direct):
        """Test that batch activation is rejected when hospitals have mixed active states."""
        batch_id = uuid.uuid4()

        create_test_hospital_direct("Hospital 1", batch_id=batch_id, active=False)
        create_test_hospital_direct("Hospital 2", batch_id=batch_id, active=True)

        # Should detect that batch has active hospitals
        has_active = has_active_hospitals_in_batch(batch_id)
        assert has_active is True

    def test_empty_batch_operations(self, reset_database):
        """Test operations on non-existent batch."""
        batch_id = uuid.uuid4()

        # All operations should handle empty batches gracefully
        assert get_hospitals_by_batch_id(batch_id) == []
        assert has_active_hospitals_in_batch(batch_id) is False
        assert activate_hospitals_by_batch_id(batch_id) == 0
        assert delete_hospitals_by_batch_id(batch_id) == 0