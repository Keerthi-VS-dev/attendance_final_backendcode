from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    date_of_birth = Column(Date)
    joining_date = Column(Date, nullable=False)
    designation = Column(String(100))
    department_id = Column(Integer, ForeignKey("departments.department_id"))
    manager_id = Column(Integer, ForeignKey("employees.employee_id"))
    role = Column(Enum(UserRole), nullable=False, default=UserRole.EMPLOYEE)
    profile_picture_url = Column(String(500))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    department = relationship("Department", back_populates="employees")
    manager = relationship("Employee", remote_side=[employee_id], backref="subordinates")
    
    # Attendance
    attendance_records = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")
    
    # Leaves
    leave_balances = relationship("LeaveBalance", back_populates="employee", cascade="all, delete-orphan")
    leave_applications = relationship(
        "LeaveApplication",
        foreign_keys="LeaveApplication.employee_id",
        back_populates="employee",
        cascade="all, delete-orphan"
    )
    approved_leaves = relationship(
        "LeaveApplication",
        foreign_keys="LeaveApplication.approved_by",
        back_populates="approver"
    )
    
    # Raves
    raves_sent = relationship(
        "Rave",
        foreign_keys="Rave.from_employee_id",
        back_populates="sender",
        cascade="all, delete-orphan"
    )
    raves_received = relationship(
        "Rave",
        foreign_keys="Rave.to_employee_id",
        back_populates="recipient",
        cascade="all, delete-orphan"
    )
    
    # Notifications
    notifications = relationship("Notification", back_populates="employee", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        """Return full name of employee"""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Employee(id={self.employee_id}, name={self.full_name}, role={self.role})>"
