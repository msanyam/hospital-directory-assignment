from typing import List, Optional
from models import Hospital

hospitals_db: List[Hospital] = []
next_id: int = 1


def get_all_hospitals() -> List[Hospital]:
    return hospitals_db


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
    for i, hospital in enumerate(hospitals_db):
        if hospital.id == hospital_id:
            hospitals_db[i] = updated_hospital
            return updated_hospital
    return None


def delete_hospital(hospital_id: int) -> bool:
    global hospitals_db
    initial_len = len(hospitals_db)
    hospitals_db = [hospital for hospital in hospitals_db if hospital.id != hospital_id]
    return len(hospitals_db) < initial_len
