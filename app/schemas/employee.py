from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import date, datetime
from app.models.employee import UserRole


# Base Schema
class EmployeeBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    designation: Optional[str] = Field(None, max_length=100)
    department_id: Optional[int] = None
    manager_id: Optional[int] = None


# Create Schema
class EmployeeCreate(EmployeeBase):
    password: str = Field(..., min_length=6)
    joining_date: date
    role: UserRole = UserRole.EMPLOYEE

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


# Update Schema
class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    designation: Optional[str] = Field(None, max_length=100)
    department_id: Optional[int] = None
    manager_id: Optional[int] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    profile_picture_url: Optional[str] = None


# Response Schema
class EmployeeResponse(EmployeeBase):
    employee_id: int
    joining_date: date
    role: UserRole
    is_active: bool
    profile_picture_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Detailed Response with relationships
class EmployeeDetail(EmployeeResponse):
    department_name: Optional[str] = None
    manager_name: Optional[str] = None
    rave_count: int = 0

    class Config:
        from_attributes = True


# Login Schema
class EmployeeLogin(BaseModel):
    email: EmailStr
    password: str


# Token Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    employee_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[UserRole] = None


# Change Password Schema
class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
