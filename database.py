from typing import List, Optional
from models import Hospital
from uuid import UUID
from collections import deque

# FIFO storage with maximum capacity
MAX_HOSPITALS = 10000
hospitals_db: deque = deque(maxlen=MAX_HOSPITALS)
next_id: int = 1


def get_all_hospitals() -> List[Hospital]:
    return list(hospitals_db)


def get_hospitals_by_batch_id(batch_id: UUID) -> List[Hospital]:
    return [hospital for hospital in hospitals_db if hospital.creation_batch_id == batch_id]


def get_hospital_by_id(hospital_id: int) -> Optional[Hospital]:
    for hospital in hospitals_db:
        if hospital.id == hospital_id:
            return hospital
    return None


def create_hospital(hospital: Hospital) -> Hospital:
    global next_id
    hospital.id = next_id
    next_id += 1
    hospitals_db.append(hospital)
    return hospital


def update_hospital(hospital_id: int, updated_hospital: Hospital) -> Optional[Hospital]:
    global hospitals_db
    # Convert to list for modification
    hospital_list = list(hospitals_db)
    for i, hospital in enumerate(hospital_list):
        if hospital.id == hospital_id:
            hospital_list[i] = updated_hospital
            # Convert back to deque
            hospitals_db = deque(hospital_list, maxlen=MAX_HOSPITALS)
            return updated_hospital
    return None


def delete_hospital(hospital_id: int) -> bool:
    global hospitals_db
    initial_len = len(hospitals_db)
    # Convert to list, filter, and convert back to deque
    filtered_hospitals = [hospital for hospital in hospitals_db if hospital.id != hospital_id]
    hospitals_db = deque(filtered_hospitals, maxlen=MAX_HOSPITALS)
    return len(hospitals_db) < initial_len


def delete_hospitals_by_batch_id(batch_id: UUID) -> int:
    global hospitals_db
    initial_len = len(hospitals_db)
    # Convert to list, filter, and convert back to deque
    filtered_hospitals = [hospital for hospital in hospitals_db if hospital.creation_batch_id != batch_id]
    hospitals_db = deque(filtered_hospitals, maxlen=MAX_HOSPITALS)
    return initial_len - len(hospitals_db)


def has_active_hospitals_in_batch(batch_id: UUID) -> bool:
    for hospital in hospitals_db:
        if hospital.creation_batch_id == batch_id and hospital.active:
            return True
    return False


def activate_hospitals_by_batch_id(batch_id: UUID) -> int:
    count = 0
    for hospital in hospitals_db:
        if hospital.creation_batch_id == batch_id and not hospital.active:
            hospital.active = True
            count += 1
    return count
