from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class RaveCategory(Base):
    __tablename__ = "rave_categories"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    icon = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    raves = relationship("Rave", back_populates="category")

    def __repr__(self):
        return f"<RaveCategory(id={self.category_id}, name={self.category_name})>"


class Rave(Base):
    __tablename__ = "raves"
    __table_args__ = (
        CheckConstraint('from_employee_id != to_employee_id', name='check_different_employees'),
    )

    rave_id = Column(Integer, primary_key=True, index=True)
    from_employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False, index=True)
    to_employee_id = Column(Integer, ForeignKey("employees.employee_id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("rave_categories.category_id"))
    message = Column(Text, nullable=False)
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    sender = relationship("Employee", foreign_keys=[from_employee_id], back_populates="raves_sent")
    recipient = relationship("Employee", foreign_keys=[to_employee_id], back_populates="raves_received")
    category = relationship("RaveCategory", back_populates="raves")

    def __repr__(self):
        return f"<Rave(id={self.rave_id}, from={self.from_employee_id}, to={self.to_employee_id})>"
