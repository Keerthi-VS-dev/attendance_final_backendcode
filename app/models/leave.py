from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime, ForeignKey, Enum, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LeaveType(Base):
    __tablename__ = "leave_types"

    leave_type_id = Column(Integer, primary_key=True, index=True)
    type_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    max_days_per_year = Column(Integer)
    requires_approval = Column(Boolean, default=True)
    is_paid = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    leave_balances = relationship("LeaveBalance", back_populates="leave_type")
    leave_applications = relationship("LeaveApplication", back_populates="leave_type")

    def __repr__(self):
        return f"<LeaveType(id={self.leave_type_id}, name={self.type_name})>"


class LeaveBalance(Base):
    __tablename__ = "leave_balance"
    __table_args__ = (
        UniqueConstraint('employee_id', 'leave_type_id', 'year', name='unique_employee_leave_year'),
    )

    balance_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False, index=True)
    leave_type_id = Column(Integer, ForeignKey("leave_types.leave_type_id"), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    total_allocated = Column(Numeric(5, 2), nullable=False)
    used_days = Column(Numeric(5, 2), default=0)
    remaining_days = Column(Numeric(5, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    employee = relationship("Employee", back_populates="leave_balances")
    leave_type = relationship("LeaveType", back_populates="leave_balances")

    def __repr__(self):
        return f"<LeaveBalance(id={self.balance_id}, employee_id={self.employee_id}, type={self.leave_type_id}, year={self.year})>"


class LeaveApplication(Base):
    __tablename__ = "leave_applications"

    leave_application_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False, index=True)
    leave_type_id = Column(Integer, ForeignKey("leave_types.leave_type_id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Numeric(5, 2), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING, nullable=False, index=True)
    approved_by = Column(Integer, ForeignKey("employees.employee_id"))
    applied_on = Column(DateTime(timezone=True), server_default=func.now())
    approved_rejected_on = Column(DateTime(timezone=True))
    rejection_reason = Column(Text)
    attachments = Column(Text)  # JSON or comma-separated URLs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="leave_applications")
    leave_type = relationship("LeaveType", back_populates="leave_applications")
    approver = relationship("Employee", foreign_keys=[approved_by], back_populates="approved_leaves")

    def __repr__(self):
        return f"<LeaveApplication(id={self.leave_application_id}, employee_id={self.employee_id}, status={self.status})>"
