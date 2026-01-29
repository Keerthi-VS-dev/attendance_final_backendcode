from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class NotificationType(str, enum.Enum):
    LEAVE = "leave"
    ATTENDANCE = "attendance"
    RAVE = "rave"
    SYSTEM = "system"


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    is_read = Column(Boolean, default=False, index=True)
    link = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    employee = relationship("Employee", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.notification_id}, employee_id={self.employee_id}, type={self.type})>"
