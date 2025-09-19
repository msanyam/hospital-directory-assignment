import pytest
import uuid
from collections import deque
from app import database
from app.models import Hospital
from app.config import MAX_TOTAL_HOSPITALS

class TestDatabaseCRUD:
    """Test basic CRUD operations in the database module."""

    def test_create_hospital(self):
        """Test creating a hospital."""
        hospital = Hospital(
            id=0,  # Will be set by create_hospital
            name="Test Hospital",
            address="123 Main St",
            phone="555-1234",
            active=True
        )
        created = database.create_hospital(hospital)

        assert created.id == 1
        assert created.name == "Test Hospital"
        assert created.address == "123 Main St"
        assert created.phone == "555-1234"
        assert created.active is True
        assert len(database.hospitals_db) == 1

    def test_get_hospital_by_id(self):
        """Test retrieving a hospital by ID."""
        # Create a hospital first
        hospital = Hospital(id=0, name="Test", address="123 Main St", active=True)
        created = database.create_hospital(hospital)

        # Retrieve it
        retrieved = database.get_hospital_by_id(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Test"

    def test_get_hospital_by_id_not_found(self):
        """Test retrieving a non-existent hospital."""
        result = database.get_hospital_by_id(999)
        assert result is None

    def test_get_all_hospitals(self):
        """Test retrieving all hospitals."""
        # Initially empty
        hospitals = database.get_all_hospitals()
        assert len(hospitals) == 0

        # Add hospitals
        for i in range(3):
            hospital = Hospital(
                id=0,
                name=f"Hospital {i+1}",
                address=f"{i+1}23 Main St",
                active=True
            )
            database.create_hospital(hospital)

        hospitals = database.get_all_hospitals()
        assert len(hospitals) == 3
        assert all(isinstance(h, Hospital) for h in hospitals)

    def test_update_hospital(self):
        """Test updating a hospital."""
        # Create a hospital
        hospital = Hospital(id=0, name="Original", address="123 Main St", active=True)
        created = database.create_hospital(hospital)

        # Update it
        created.name = "Updated Name"
        created.phone = "555-NEW1"
        updated = database.update_hospital(created.id, created)

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.phone == "555-NEW1"

        # Verify it's updated in database
        retrieved = database.get_hospital_by_id(created.id)
        assert retrieved.name == "Updated Name"

    def test_update_hospital_not_found(self):
        """Test updating a non-existent hospital."""
        hospital = Hospital(id=999, name="Ghost", address="Nowhere", active=True)
        result = database.update_hospital(999, hospital)
        assert result is None

    def test_delete_hospital(self):
        """Test deleting a hospital."""
        # Create a hospital
        hospital = Hospital(id=0, name="To Delete", address="123 Main St", active=True)
        created = database.create_hospital(hospital)

        assert len(database.hospitals_db) == 1

        # Delete it
        result = database.delete_hospital(created.id)
        assert result is True
        assert len(database.hospitals_db) == 0

        # Verify it's gone
        retrieved = database.get_hospital_by_id(created.id)
        assert retrieved is None

    def test_delete_hospital_not_found(self):
        """Test deleting a non-existent hospital."""
        result = database.delete_hospital(999)
        assert result is False


class TestBatchOperations:
    """Test batch-related database operations."""

    def test_get_hospitals_by_batch_id(self):
        """Test retrieving hospitals by batch ID."""
        batch_id = uuid.uuid4()

        # Create hospitals with the same batch ID
        for i in range(3):
            hospital = Hospital(
                id=0,
                name=f"Batch Hospital {i+1}",
                address=f"{i+1}23 Main St",
                creation_batch_id=batch_id,
                active=False
            )
            database.create_hospital(hospital)

        # Create one hospital without batch ID
        hospital = Hospital(id=0, name="No Batch", address="999 Other St", active=True)
        database.create_hospital(hospital)

        # Get hospitals by batch ID
        batch_hospitals = database.get_hospitals_by_batch_id(batch_id)
        assert len(batch_hospitals) == 3
        assert all(h.creation_batch_id == batch_id for h in batch_hospitals)

    def test_get_hospitals_by_batch_id_empty(self):
        """Test retrieving hospitals by non-existent batch ID."""
        batch_id = uuid.uuid4()
        hospitals = database.get_hospitals_by_batch_id(batch_id)
        assert len(hospitals) == 0

    def test_delete_hospitals_by_batch_id(self):
        """Test deleting hospitals by batch ID."""
        batch_id = uuid.uuid4()

        # Create batch hospitals
        for i in range(3):
            hospital = Hospital(
                id=0,
                name=f"Batch Hospital {i+1}",
                address=f"{i+1}23 Main St",
                creation_batch_id=batch_id,
                active=False
            )
            database.create_hospital(hospital)

        # Create non-batch hospital
        hospital = Hospital(id=0, name="Keep Me", address="999 Safe St", active=True)
        database.create_hospital(hospital)

        assert len(database.hospitals_db) == 4

        # Delete batch
        deleted_count = database.delete_hospitals_by_batch_id(batch_id)
        assert deleted_count == 3
        assert len(database.hospitals_db) == 1

        # Verify only non-batch hospital remains
        remaining = database.get_all_hospitals()
        assert len(remaining) == 1
        assert remaining[0].name == "Keep Me"

    def test_delete_hospitals_by_batch_id_empty(self):
        """Test deleting hospitals by non-existent batch ID."""
        batch_id = uuid.uuid4()
        deleted_count = database.delete_hospitals_by_batch_id(batch_id)
        assert deleted_count == 0

    def test_has_active_hospitals_in_batch(self):
        """Test checking if batch has active hospitals."""
        batch_id = uuid.uuid4()

        # Create inactive hospitals
        for i in range(2):
            hospital = Hospital(
                id=0,
                name=f"Inactive {i+1}",
                address=f"{i+1}23 Main St",
                creation_batch_id=batch_id,
                active=False
            )
            database.create_hospital(hospital)

        # Should be False (no active hospitals)
        assert database.has_active_hospitals_in_batch(batch_id) is False

        # Add one active hospital to the batch
        hospital = Hospital(
            id=0,
            name="Active One",
            address="999 Active St",
            creation_batch_id=batch_id,
            active=True
        )
        database.create_hospital(hospital)

        # Should be True now
        assert database.has_active_hospitals_in_batch(batch_id) is True

    def test_has_active_hospitals_in_batch_empty(self):
        """Test checking active hospitals in non-existent batch."""
        batch_id = uuid.uuid4()
        assert database.has_active_hospitals_in_batch(batch_id) is False

    def test_activate_hospitals_by_batch_id(self):
        """Test activating hospitals by batch ID."""
        batch_id = uuid.uuid4()

        # Create inactive hospitals
        for i in range(3):
            hospital = Hospital(
                id=0,
                name=f"To Activate {i+1}",
                address=f"{i+1}23 Main St",
                creation_batch_id=batch_id,
                active=False
            )
            database.create_hospital(hospital)

        # Activate them
        activated_count = database.activate_hospitals_by_batch_id(batch_id)
        assert activated_count == 3

        # Verify they're all active
        batch_hospitals = database.get_hospitals_by_batch_id(batch_id)
        assert all(h.active for h in batch_hospitals)

    def test_activate_hospitals_by_batch_id_mixed(self):
        """Test activating hospitals when some are already active."""
        batch_id = uuid.uuid4()

        # Create mix of active and inactive
        hospital1 = Hospital(
            id=0, name="Already Active", address="1 Main St",
            creation_batch_id=batch_id, active=True
        )
        hospital2 = Hospital(
            id=0, name="To Activate", address="2 Main St",
            creation_batch_id=batch_id, active=False
        )
        database.create_hospital(hospital1)
        database.create_hospital(hospital2)

        # Should only activate the inactive one
        activated_count = database.activate_hospitals_by_batch_id(batch_id)
        assert activated_count == 1


class TestFIFOBehavior:
    """Test FIFO behavior with maximum capacity."""

    def test_fifo_storage_limit(self):
        """Test that storage respects FIFO limit."""
        # Save original database
        original_db = database.hospitals_db
        original_next_id = database.next_id

        try:
            # Set small limit for testing
            test_limit = 5
            database.hospitals_db = deque(maxlen=test_limit)
            database.next_id = 1

            # Add 5 hospitals
            for i in range(5):
                hospital = Hospital(
                    id=0,
                    name=f"Hospital {i+1}",
                    address=f"{i+1}23 Main St",
                    active=True
                )
                database.create_hospital(hospital)

            assert len(database.hospitals_db) == 5

            # Add one more - should evict the first
            hospital = Hospital(
                id=0,
                name="Hospital 6",
                address="623 Main St",
                active=True
            )
            database.create_hospital(hospital)

            # Still 5 hospitals, but first one should be gone
            assert len(database.hospitals_db) == 5
            hospitals = database.get_all_hospitals()
            names = [h.name for h in hospitals]
            assert "Hospital 1" not in names  # First one evicted
            assert "Hospital 6" in names      # New one added

        finally:
            # Restore original database
            database.hospitals_db = original_db
            database.next_id = original_next_id

    def test_operations_with_deque(self):
        """Test that all operations work correctly with deque."""
        # Save original database
        original_db = database.hospitals_db
        original_next_id = database.next_id

        try:
            # Set small limit for testing
            database.hospitals_db = deque(maxlen=3)
            database.next_id = 1

            # Create hospitals
            hospitals = []
            for i in range(3):
                hospital = Hospital(
                    id=0,
                    name=f"Test {i+1}",
                    address=f"{i+1}23 Main St",
                    active=True
                )
                created = database.create_hospital(hospital)
                hospitals.append(created)

            # Test retrieval
            assert len(database.get_all_hospitals()) == 3
            assert database.get_hospital_by_id(hospitals[1].id) is not None

            # Test update
            hospitals[1].name = "Updated"
            updated = database.update_hospital(hospitals[1].id, hospitals[1])
            assert updated.name == "Updated"

            # Test deletion
            deleted = database.delete_hospital(hospitals[0].id)
            assert deleted is True
            assert len(database.get_all_hospitals()) == 2

        finally:
            # Restore original database
            database.hospitals_db = original_db
            database.next_id = original_next_id

    def test_id_generation_continues(self):
        """Test that ID generation continues even with FIFO eviction."""
        # Save original database
        original_db = database.hospitals_db
        original_next_id = database.next_id

        try:
            # Set small limit for testing
            database.hospitals_db = deque(maxlen=2)
            database.next_id = 1

            # Create 3 hospitals (will evict first)
            ids = []
            for i in range(3):
                hospital = Hospital(
                    id=0,
                    name=f"Hospital {i+1}",
                    address=f"{i+1}23 Main St",
                    active=True
                )
                created = database.create_hospital(hospital)
                ids.append(created.id)

            # IDs should be 1, 2, 3 even though first was evicted
            assert ids == [1, 2, 3]

            # Only hospitals 2 and 3 should remain
            hospitals = database.get_all_hospitals()
            assert len(hospitals) == 2
            remaining_ids = [h.id for h in hospitals]
            assert 1 not in remaining_ids
            assert 2 in remaining_ids
            assert 3 in remaining_ids

        finally:
            # Restore original database
            database.hospitals_db = original_db
            database.next_id = original_next_id