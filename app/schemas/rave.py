from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


# Rave Category Schemas
class RaveCategoryBase(BaseModel):
    category_name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    icon: Optional[str] = None


class RaveCategoryCreate(RaveCategoryBase):
    pass


class RaveCategoryResponse(RaveCategoryBase):
    category_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Rave Schemas
class RaveBase(BaseModel):
    to_employee_id: int
    category_id: Optional[int] = None
    message: str = Field(..., min_length=1)
    is_anonymous: bool = False


class RaveCreate(RaveBase):
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('Message cannot be empty')
        return v.strip()


class RaveResponse(RaveBase):
    rave_id: int
    from_employee_id: int
    created_at: datetime
    
    # Additional fields
    sender_name: Optional[str] = None
    recipient_name: Optional[str] = None
    category_name: Optional[str] = None
    sender_designation: Optional[str] = None
    recipient_designation: Optional[str] = None

    class Config:
        from_attributes = True
