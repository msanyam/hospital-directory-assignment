from fastapi import FastAPI, HTTPException
from typing import List
from models import Hospital, HospitalCreate, HospitalUpdate
import database
import os
import uvicorn

app = FastAPI()


@app.get("/")
def health_check():
    return {"status": "OK"}


@app.post("/hospitals/", response_model=Hospital)
def create_hospital(hospital: HospitalCreate):
    new_hospital = Hospital(
        id=0,  # Temporary ID, will be set by database.create_hospital
        name=hospital.name,
        address=hospital.address,
        phone=hospital.phone,
    )
    created = database.create_hospital(new_hospital)
    return created


@app.get("/hospitals/", response_model=List[Hospital])
def get_all_hospitals():
    return database.get_all_hospitals()


@app.get("/hospitals/{hospital_id}", response_model=Hospital)
def get_hospital_by_id(hospital_id: int):
    hospital = database.get_hospital_by_id(hospital_id)
    if hospital is None:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital


@app.put("/hospitals/{hospital_id}", response_model=Hospital)
def update_hospital(hospital_id: int, hospital_update: HospitalUpdate):
    existing_hospital = database.get_hospital_by_id(hospital_id)
    if existing_hospital is None:
        raise HTTPException(status_code=404, detail="Hospital not found")

    update_data = hospital_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(existing_hospital, key, value)

    updated = database.update_hospital(hospital_id, existing_hospital)
    if updated is None:
        raise HTTPException(status_code=500, detail="Failed to update hospital")
    return updated


@app.delete("/hospitals/{hospital_id}", status_code=204)
def delete_hospital(hospital_id: int):
    if not database.delete_hospital(hospital_id):
        raise HTTPException(status_code=404, detail="Hospital not found")
    return


if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
