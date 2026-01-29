from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time, datetime
from decimal import Decimal
from app.models.attendance import AttendanceStatus


class AttendanceBase(BaseModel):
    attendance_date: date
    status: AttendanceStatus = AttendanceStatus.PRESENT


class AttendanceCreate(AttendanceBase):
    employee_id: int
    clock_in_time: Optional[time] = None
    clock_out_time: Optional[time] = None
    notes: Optional[str] = None
    location: Optional[str] = None


class AttendanceUpdate(BaseModel):
    clock_in_time: Optional[time] = None
    clock_out_time: Optional[time] = None
    status: Optional[AttendanceStatus] = None
    notes: Optional[str] = None
    location: Optional[str] = None


class AttendanceResponse(AttendanceBase):
    attendance_id: int
    employee_id: int
    clock_in_time: Optional[time] = None
    clock_out_time: Optional[time] = None
    hours_worked: Optional[Decimal] = None
    notes: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Additional fields for enriched response
    employee_name: Optional[str] = None

    class Config:
        from_attributes = True


class ClockInRequest(BaseModel):
    location: Optional[str] = None


class ClockOutRequest(BaseModel):
    location: Optional[str] = None
