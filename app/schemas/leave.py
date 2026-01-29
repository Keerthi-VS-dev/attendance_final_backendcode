from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal
from app.models.leave import LeaveStatus


# Leave Type Schemas
class LeaveTypeBase(BaseModel):
    type_name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    max_days_per_year: Optional[int] = None
    requires_approval: bool = True
    is_paid: bool = True


class LeaveTypeCreate(LeaveTypeBase):
    pass


class LeaveTypeResponse(LeaveTypeBase):
    leave_type_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Leave Balance Schemas
class LeaveBalanceResponse(BaseModel):
    balance_id: int
    employee_id: int
    leave_type_id: int
    leave_type_name: Optional[str] = None
    year: int
    total_allocated: Decimal
    used_days: Decimal
    remaining_days: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Leave Application Schemas
class LeaveApplicationBase(BaseModel):
    leave_type_id: int
    start_date: date
    end_date: date
    reason: str = Field(..., min_length=1)
    attachments: Optional[str] = None

    @field_validator('end_date')
    @classmethod
    def validate_dates(cls, v, info):
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError('End date must be after or equal to start date')
        return v


class LeaveApplicationCreate(LeaveApplicationBase):
    pass


class LeaveApplicationUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = Field(None, min_length=1)
    attachments: Optional[str] = None


class LeaveApplicationResponse(LeaveApplicationBase):
    leave_application_id: int
    employee_id: int
    total_days: Decimal
    status: LeaveStatus
    approved_by: Optional[int] = None
    applied_on: datetime
    approved_rejected_on: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Additional fields
    employee_name: Optional[str] = None
    leave_type_name: Optional[str] = None
    approver_name: Optional[str] = None

    class Config:
        from_attributes = True


class LeaveApprovalRequest(BaseModel):
    status: LeaveStatus = Field(..., description="approved or rejected")
    rejection_reason: Optional[str] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in [LeaveStatus.APPROVED, LeaveStatus.REJECTED]:
            raise ValueError('Status must be either approved or rejected')
        return v
