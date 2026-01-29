from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class HolidayBase(BaseModel):
    holiday_date: date
    holiday_name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_optional: bool = False


class HolidayCreate(HolidayBase):
    pass


class HolidayResponse(HolidayBase):
    holiday_id: int
    created_at: datetime

    class Config:
        from_attributes = True
