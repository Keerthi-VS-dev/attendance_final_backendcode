from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DepartmentBase(BaseModel):
    department_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    department_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class DepartmentResponse(DepartmentBase):
    department_id: int
    created_at: datetime
    updated_at: datetime
    employee_count: Optional[int] = 0

    class Config:
        from_attributes = True
