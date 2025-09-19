from fastapi import FastAPI, HTTPException, Request
from typing import List
from .models import Hospital, HospitalCreate, HospitalUpdate
from . import database
from .config import (
    APP_NAME, DESCRIPTION, VERSION, MAX_BATCH_SIZE,
    SLOW_TASK_DELAY_SECONDS, RATE_LIMITS, get_port
)
from uuid import UUID
import uvicorn
import time
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title=APP_NAME,
    description=DESCRIPTION,
    version=VERSION
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def slow_running_task():
    """Simulates a slow-running task with configurable delay."""
    time.sleep(SLOW_TASK_DELAY_SECONDS)


@app.get("/")
@limiter.limit(RATE_LIMITS["health_check"])
def health_check(request: Request):
    return {"status": "OK"}


@app.post("/hospitals/", response_model=Hospital)
@limiter.limit(RATE_LIMITS["create_hospital"])
def create_hospital(request: Request, hospital: HospitalCreate):
    # Check if adding this hospital would exceed batch size limit
    if hospital.creation_batch_id:
        existing_batch = database.get_hospitals_by_batch_id(hospital.creation_batch_id)
        if len(existing_batch) >= MAX_BATCH_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Batch cannot exceed {MAX_BATCH_SIZE} hospitals",
            )

    # Execute slow running task
    slow_running_task()

    new_hospital = Hospital(
        id=0,  # Temporary ID, will be set by database.create_hospital
        name=hospital.name,
        address=hospital.address,
        phone=hospital.phone,
        creation_batch_id=hospital.creation_batch_id,
        active=hospital.creation_batch_id is None,  # False if batch_id provided, True otherwise
    )
    created = database.create_hospital(new_hospital)
    return created


@app.get("/hospitals/", response_model=List[Hospital])
@limiter.limit(RATE_LIMITS["get_hospitals"])
def get_all_hospitals(request: Request):
    return database.get_all_hospitals()


@app.get("/hospitals/{hospital_id}", response_model=Hospital)
@limiter.limit(RATE_LIMITS["get_hospital_by_id"])
def get_hospital_by_id(request: Request, hospital_id: int):
    hospital = database.get_hospital_by_id(hospital_id)
    if hospital is None:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital


@app.put("/hospitals/{hospital_id}", response_model=Hospital)
@limiter.limit(RATE_LIMITS["update_hospital"])
def update_hospital(
    request: Request, hospital_id: int, hospital_update: HospitalUpdate
):
    existing_hospital = database.get_hospital_by_id(hospital_id)
    if existing_hospital is None:
        raise HTTPException(status_code=404, detail="Hospital not found")

    update_data = hospital_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing_hospital, key, value)

    updated = database.update_hospital(hospital_id, existing_hospital)
    if updated is None:
        raise HTTPException(status_code=500, detail="Failed to update hospital")
    return updated


@app.delete("/hospitals/{hospital_id}", status_code=204)
@limiter.limit(RATE_LIMITS["delete_hospital"])
def delete_hospital(request: Request, hospital_id: int):
    if not database.delete_hospital(hospital_id):
        raise HTTPException(status_code=404, detail="Hospital not found")
    return


@app.get("/hospitals/batch/{batch_id}", response_model=List[Hospital])
@limiter.limit(RATE_LIMITS["get_batch"])
def get_hospitals_by_batch_id(request: Request, batch_id: UUID):
    hospitals = database.get_hospitals_by_batch_id(batch_id)
    if not hospitals:
        raise HTTPException(
            status_code=404, detail="No hospitals found with the specified batch ID"
        )
    return hospitals


@app.delete("/hospitals/batch/{batch_id}")
@limiter.limit(RATE_LIMITS["delete_batch"])
def delete_hospitals_by_batch(request: Request, batch_id: UUID):
    deleted_count = database.delete_hospitals_by_batch_id(batch_id)
    if deleted_count == 0:
        raise HTTPException(
            status_code=404, detail="No hospitals found with the specified batch ID"
        )
    return {
        "deleted_count": deleted_count,
        "message": f"Deleted {deleted_count} hospital(s) with batch ID {batch_id}",
    }


@app.patch("/hospitals/batch/{batch_id}/activate")
@limiter.limit(RATE_LIMITS["activate_batch"])
def activate_hospitals_by_batch(request: Request, batch_id: UUID):
    # Check if batch exists
    hospitals_in_batch = database.get_hospitals_by_batch_id(batch_id)
    if not hospitals_in_batch:
        raise HTTPException(
            status_code=404, detail="No hospitals found with the specified batch ID"
        )

    # Check if any hospitals in the batch are already active
    if database.has_active_hospitals_in_batch(batch_id):
        raise HTTPException(
            status_code=400,
            detail="Cannot activate batch: one or more hospitals in the batch are already active",
        )

    activated_count = database.activate_hospitals_by_batch_id(batch_id)
    return {
        "activated_count": activated_count,
        "message": f"Activated {activated_count} hospital(s) with batch ID {batch_id}",
    }


if __name__ == "__main__":
    port = get_port()
    uvicorn.run(app, host="0.0.0.0", port=port)