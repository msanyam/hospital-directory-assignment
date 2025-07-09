from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Hospital(BaseModel):
    id: int
    name: str
    address: str
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class HospitalCreate(BaseModel):
    name: str
    address: str
    phone: Optional[str] = None


class HospitalUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
