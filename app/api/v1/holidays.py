from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.models.employee import Employee
from app.models.holiday import Holiday
from app.schemas.holiday import HolidayCreate, HolidayResponse
from app.dependencies import get_current_user, get_current_admin

router = APIRouter()


@router.get("/", response_model=List[HolidayResponse])
def get_holidays(
    year: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of holidays"""
    query = db.query(Holiday)
    
    if year:
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        query = query.filter(Holiday.holiday_date.between(start_date, end_date))
    
    holidays = query.order_by(Holiday.holiday_date).offset(skip).limit(limit).all()
    
    return holidays


@router.get("/upcoming", response_model=List[HolidayResponse])
def get_upcoming_holidays(
    limit: int = Query(10, ge=1, le=50),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get upcoming holidays"""
    today = date.today()
    
    holidays = db.query(Holiday).filter(
        Holiday.holiday_date >= today
    ).order_by(Holiday.holiday_date).limit(limit).all()
    
    return holidays


@router.get("/{holiday_id}", response_model=HolidayResponse)
def get_holiday(
    holiday_id: int,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get holiday by ID"""
    holiday = db.query(Holiday).filter(Holiday.holiday_id == holiday_id).first()
    
    if not holiday:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holiday not found"
        )
    
    return holiday


@router.post("/", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
def create_holiday(
    holiday: HolidayCreate,
    current_user: Employee = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new holiday (Admin only)"""
    # Check if holiday already exists for this date
    existing = db.query(Holiday).filter(Holiday.holiday_date == holiday.holiday_date).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Holiday already exists for this date"
        )
    
    db_holiday = Holiday(**holiday.model_dump())
    db.add(db_holiday)
    db.commit()
    db.refresh(db_holiday)
    
    return db_holiday


@router.put("/{holiday_id}", response_model=HolidayResponse)
def update_holiday(
    holiday_id: int,
    holiday_update: HolidayCreate,
    current_user: Employee = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update a holiday (Admin only)"""
    holiday = db.query(Holiday).filter(Holiday.holiday_id == holiday_id).first()
    
    if not holiday:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holiday not found"
        )
    
    # Check if new date conflicts with another holiday
    if holiday_update.holiday_date != holiday.holiday_date:
        existing = db.query(Holiday).filter(
            Holiday.holiday_date == holiday_update.holiday_date,
            Holiday.holiday_id != holiday_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another holiday already exists for this date"
            )
    
    # Update fields
    for field, value in holiday_update.model_dump().items():
        setattr(holiday, field, value)
    
    db.commit()
    db.refresh(holiday)
    
    return holiday


@router.delete("/{holiday_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_holiday(
    holiday_id: int,
    current_user: Employee = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete a holiday (Admin only)"""
    holiday = db.query(Holiday).filter(Holiday.holiday_id == holiday_id).first()
    
    if not holiday:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holiday not found"
        )
    
    db.delete(holiday)
    db.commit()
    
    return None
