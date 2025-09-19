from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class Hospital(BaseModel):
    id: int
    name: str
    address: str
    phone: Optional[str] = None
    creation_batch_id: Optional[UUID] = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)


class HospitalCreate(BaseModel):
    name: str
    address: str
    phone: Optional[str] = None
    creation_batch_id: Optional[UUID] = None


class HospitalUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
