from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID


class Hospital(BaseModel):
    id: int
    name: str = Field(min_length=1)
    address: str = Field(min_length=1)
    phone: Optional[str] = None
    creation_batch_id: Optional[UUID] = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)

    @field_validator('name', 'address')
    @classmethod
    def validate_non_empty_strings(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v


class HospitalCreate(BaseModel):
    name: str = Field(min_length=1)
    address: str = Field(min_length=1)
    phone: Optional[str] = None
    creation_batch_id: Optional[UUID] = None

    @field_validator('name', 'address')
    @classmethod
    def validate_non_empty_strings(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v


class HospitalUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

    @field_validator('name', 'address')
    @classmethod
    def validate_non_empty_strings(cls, v):
        if v is not None and isinstance(v, str) and not v.strip():
            raise ValueError('Field cannot be empty or whitespace only')
        return v
