from sqlalchemy import Column, Integer, Date, Time, Text, String, DateTime, ForeignKey, Enum, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    HALF_DAY = "half_day"
    LATE = "late"
    ON_LEAVE = "on_leave"


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint('employee_id', 'attendance_date', name='unique_employee_date'),
    )

    attendance_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False, index=True)
    attendance_date = Column(Date, nullable=False, index=True)
    clock_in_time = Column(Time)
    clock_out_time = Column(Time)
    status = Column(Enum(AttendanceStatus), nullable=False, default=AttendanceStatus.PRESENT)
    hours_worked = Column(Numeric(4, 2))
    notes = Column(Text)
    location = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="attendance_records")

    def __repr__(self):
        return f"<Attendance(id={self.attendance_id}, employee_id={self.employee_id}, date={self.attendance_date}, status={self.status})>"
