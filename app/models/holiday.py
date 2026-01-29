from sqlalchemy import Column, Integer, String, Text, Date, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Holiday(Base):
    __tablename__ = "holidays"

    holiday_id = Column(Integer, primary_key=True, index=True)
    holiday_date = Column(Date, unique=True, nullable=False, index=True)
    holiday_name = Column(String(100), nullable=False)
    description = Column(Text)
    is_optional = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Holiday(id={self.holiday_id}, name={self.holiday_name}, date={self.holiday_date})>"
