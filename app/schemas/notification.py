from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.notification import NotificationType


class NotificationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    type: NotificationType
    link: Optional[str] = None


class NotificationCreate(NotificationBase):
    employee_id: int


class NotificationResponse(NotificationBase):
    notification_id: int
    employee_id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
