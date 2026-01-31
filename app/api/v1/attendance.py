from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from typing import List, Optional
from datetime import date, datetime, time as dt_time, timedelta
from app.database import get_db
from app.models.employee import Employee
from app.models.attendance import Attendance, AttendanceStatus
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
    ClockInRequest,
    ClockOutRequest
)
from app.dependencies import get_current_user, get_current_manager_or_admin
from app.config import settings

router = APIRouter()


def calculate_hours_worked(clock_in: dt_time, clock_out: dt_time) -> float:
    """Calculate hours worked between clock in and clock out times"""
    if not clock_in or not clock_out:
        return 0.0
    
    # Convert times to datetime for calculation
    today = date.today()
    dt_in = datetime.combine(today, clock_in)
    dt_out = datetime.combine(today, clock_out)
    
    # Calculate difference
    diff = dt_out - dt_in
    hours = diff.total_seconds() / 3600
    
    return round(hours, 2)


def determine_attendance_status(clock_in: dt_time, clock_out: Optional[dt_time] = None) -> AttendanceStatus:
    """Determine attendance status based on clock in time"""
    if not clock_in:
        return AttendanceStatus.ABSENT
    
    # Parse work start time from settings
    work_start = datetime.strptime(settings.WORK_START_TIME, "%H:%M").time()
    
    # Calculate late threshold
    late_threshold = datetime.combine(date.today(), work_start)
    late_threshold = (late_threshold.replace(tzinfo=None) + 
                     timedelta(minutes=settings.LATE_ARRIVAL_THRESHOLD_MINUTES)).time()
    
    if clock_in > late_threshold:
        return AttendanceStatus.LATE
    
    return AttendanceStatus.PRESENT


@router.post("/clock-in", response_model=AttendanceResponse)
def clock_in(
    request: ClockInRequest,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clock in for the day"""
    today = date.today()
    
    # Check if already clocked in today
    existing_attendance = db.query(Attendance).filter(
        and_(
            Attendance.employee_id == current_user.employee_id,
            Attendance.attendance_date == today
        )
    ).first()
    
    if existing_attendance:
        if existing_attendance.clock_in_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already clocked in today"
            )
    
    clock_in_time = datetime.now().time()
    status_value = determine_attendance_status(clock_in_time)
    
    if existing_attendance:
        # Update existing record
        existing_attendance.clock_in_time = clock_in_time
        existing_attendance.status = status_value
        existing_attendance.location = request.location
        db.commit()
        db.refresh(existing_attendance)
        attendance = existing_attendance
    else:
        # Create new attendance record
        attendance = Attendance(
            employee_id=current_user.employee_id,
            attendance_date=today,
            clock_in_time=clock_in_time,
            status=status_value,
            location=request.location
        )
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
    
    # Add employee name
    response_dict = {
        **attendance.__dict__,
        "employee_name": current_user.full_name
    }
    
    return response_dict


@router.post("/clock-out", response_model=AttendanceResponse)
def clock_out(
    request: ClockOutRequest,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clock out for the day"""
    today = date.today()
    
    # Find today's attendance record
    attendance = db.query(Attendance).filter(
        and_(
            Attendance.employee_id == current_user.employee_id,
            Attendance.attendance_date == today
        )
    ).first()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No clock-in record found for today"
        )
    
    if not attendance.clock_in_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must clock in before clocking out"
        )
    
    if attendance.clock_out_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already clocked out today"
        )
    
    # Update clock out time
    clock_out_time = datetime.now().time()
    attendance.clock_out_time = clock_out_time
    attendance.hours_worked = calculate_hours_worked(attendance.clock_in_time, clock_out_time)
    
    if request.location:
        attendance.location = request.location
    
    db.commit()
    db.refresh(attendance)
    
    # Add employee name
    response_dict = {
        **attendance.__dict__,
        "employee_name": current_user.full_name
    }
    
    return response_dict



@router.get("/my-attendance", response_model=List[AttendanceResponse])
def get_my_attendance(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=100),
    team_data: bool = Query(False),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's attendance records, or all team data if team_data=true and user is admin/manager"""
    
    # If team_data is requested, check if user is admin/manager and return all data
    if team_data:
        from app.models.employee import UserRole
        
        # Check if user has admin/manager privileges using enum comparison
        if current_user.role in (UserRole.ADMIN, UserRole.MANAGER):
            # Return all employees' attendance data
            query = db.query(Attendance)
            
            if start_date:
                query = query.filter(Attendance.attendance_date >= start_date)
            if end_date:
                query = query.filter(Attendance.attendance_date <= end_date)
            
            attendance_records = query.order_by(Attendance.attendance_date.desc()).offset(skip).limit(limit).all()
            
            # Add employee names for all records
            results = []
            for record in attendance_records:
                employee = db.query(Employee).filter(Employee.employee_id == record.employee_id).first()
                record_dict = {
                    "attendance_id": record.attendance_id,
                    "employee_id": record.employee_id,
                    "attendance_date": str(record.attendance_date),
                    "clock_in_time": str(record.clock_in_time) if record.clock_in_time else None,
                    "clock_out_time": str(record.clock_out_time) if record.clock_out_time else None,
                    "status": str(record.status),
                    "hours_worked": float(record.hours_worked) if record.hours_worked else 0.0,
                    "location": record.location,
                    "employee_name": employee.full_name if employee else "Unknown",
                    "employee": {
                        "employee_id": employee.employee_id,
                        "full_name": employee.full_name,
                        "first_name": employee.first_name,
                        "last_name": employee.last_name,
                        "designation": employee.designation,
                        "department": employee.department.department_name if employee and employee.department else None
                    } if employee else None
                }
                results.append(record_dict)
            
            return results
    
    # Default behavior - return current user's attendance
    query = db.query(Attendance).filter(Attendance.employee_id == current_user.employee_id)
    
    if start_date:
        query = query.filter(Attendance.attendance_date >= start_date)
    
    if end_date:
        query = query.filter(Attendance.attendance_date <= end_date)
    
    attendance_records = query.order_by(Attendance.attendance_date.desc()).offset(skip).limit(limit).all()
    
    # Add employee name
    results = []
    for record in attendance_records:
        record_dict = {
            "attendance_id": record.attendance_id,
            "employee_id": record.employee_id,
            "attendance_date": str(record.attendance_date),
            "clock_in_time": str(record.clock_in_time) if record.clock_in_time else None,
            "clock_out_time": str(record.clock_out_time) if record.clock_out_time else None,
            "status": str(record.status),
            "hours_worked": float(record.hours_worked) if record.hours_worked else 0.0,
            "location": record.location,
            "employee_name": current_user.full_name
        }
        results.append(record_dict)
    
    return results


@router.get("/employee/{employee_id}", response_model=List[AttendanceResponse])
def get_employee_attendance(
    employee_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=100),
    current_user: Employee = Depends(get_current_manager_or_admin),
    db: Session = Depends(get_db)
):
    """Get attendance records for a specific employee (Manager/Admin only)"""
    # Check if employee exists
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    query = db.query(Attendance).filter(Attendance.employee_id == employee_id)
    
    if start_date:
        query = query.filter(Attendance.attendance_date >= start_date)
    
    if end_date:
        query = query.filter(Attendance.attendance_date <= end_date)
    
    attendance_records = query.order_by(Attendance.attendance_date.desc()).offset(skip).limit(limit).all()
    
    # Add employee name
    results = []
    for record in attendance_records:
        record_dict = {
            **record.__dict__,
            "employee_name": employee.full_name
        }
        results.append(record_dict)
    
    return results


@router.get("/today", response_model=AttendanceResponse)
def get_today_attendance(
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get today's attendance record"""
    today = date.today()
    
    attendance = db.query(Attendance).filter(
        and_(
            Attendance.employee_id == current_user.employee_id,
            Attendance.attendance_date == today
        )
    ).first()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No attendance record for today"
        )
    
    # Add employee name
    response_dict = {
        **attendance.__dict__,
        "employee_name": current_user.full_name
    }
    
    return response_dict


@router.post("/", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance(
    attendance: AttendanceCreate,
    current_user: Employee = Depends(get_current_manager_or_admin),
    db: Session = Depends(get_db)
):
    """Create attendance record manually (Manager/Admin only)"""
    # Check if employee exists
    employee = db.query(Employee).filter(Employee.employee_id == attendance.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Check if attendance already exists for this date
    existing = db.query(Attendance).filter(
        and_(
            Attendance.employee_id == attendance.employee_id,
            Attendance.attendance_date == attendance.attendance_date
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendance record already exists for this date"
        )
    
    # Calculate hours worked if both times provided
    hours_worked = None
    if attendance.clock_in_time and attendance.clock_out_time:
        hours_worked = calculate_hours_worked(attendance.clock_in_time, attendance.clock_out_time)
    
    db_attendance = Attendance(
        **attendance.model_dump(),
        hours_worked=hours_worked
    )
    
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    
    # Add employee name
    response_dict = {
        **db_attendance.__dict__,
        "employee_name": employee.full_name
    }
    
    return response_dict


@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(
    attendance_id: int,
    attendance_update: AttendanceUpdate,
    current_user: Employee = Depends(get_current_manager_or_admin),
    db: Session = Depends(get_db)
):
    """Update attendance record (Manager/Admin only)"""
    attendance = db.query(Attendance).filter(Attendance.attendance_id == attendance_id).first()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    
    # Update fields
    update_data = attendance_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(attendance, field, value)
    
    # Recalculate hours worked if times changed
    if attendance.clock_in_time and attendance.clock_out_time:
        attendance.hours_worked = calculate_hours_worked(attendance.clock_in_time, attendance.clock_out_time)
    
    db.commit()
    db.refresh(attendance)
    
    # Get employee name
    employee = db.query(Employee).filter(Employee.employee_id == attendance.employee_id).first()
    
    response_dict = {
        **attendance.__dict__,
        "employee_name": employee.full_name if employee else None
    }
    
    return response_dict


@router.get("/statistics/monthly")
def get_monthly_statistics(
    year: int = Query(..., ge=2000),
    month: int = Query(..., ge=1, le=12),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly attendance statistics for current user"""
    # Get attendance records for the month
    attendance_records = db.query(Attendance).filter(
        and_(
            Attendance.employee_id == current_user.employee_id,
            extract('year', Attendance.attendance_date) == year,
            extract('month', Attendance.attendance_date) == month
        )
    ).all()
    
    # Calculate statistics
    total_days = len(attendance_records)
    present_days = len([r for r in attendance_records if r.status == AttendanceStatus.PRESENT])
    late_days = len([r for r in attendance_records if r.status == AttendanceStatus.LATE])
    absent_days = len([r for r in attendance_records if r.status == AttendanceStatus.ABSENT])
    half_days = len([r for r in attendance_records if r.status == AttendanceStatus.HALF_DAY])
    on_leave_days = len([r for r in attendance_records if r.status == AttendanceStatus.ON_LEAVE])
    
    total_hours = sum([float(r.hours_worked or 0) for r in attendance_records])
    
    return {
        "year": year,
        "month": month,
        "total_days": total_days,
        "present_days": present_days,
        "late_days": late_days,
        "absent_days": absent_days,
        "half_days": half_days,
        "on_leave_days": on_leave_days,
        "total_hours_worked": round(total_hours, 2)
    }

@router.get("/team-attendance", response_model=List[AttendanceResponse])
def get_team_attendance(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get team attendance records (Admin/Manager only) - dedicated endpoint"""
    from app.models.employee import UserRole
    
    print(f"DEBUG: Team attendance endpoint called by user {current_user.employee_id}")
    print(f"DEBUG: User role: {current_user.role}")
    print(f"DEBUG: Is admin: {current_user.role == UserRole.ADMIN}")
    print(f"DEBUG: Is manager: {current_user.role == UserRole.MANAGER}")
    
    # Check if user has admin/manager privileges
    if current_user.role not in (UserRole.ADMIN, UserRole.MANAGER):
        print("DEBUG: User is not admin/manager - returning only their data")
        # Return only current user's data for employees
        query = db.query(Attendance).filter(Attendance.employee_id == current_user.employee_id)
        
        if start_date:
            query = query.filter(Attendance.attendance_date >= start_date)
        if end_date:
            query = query.filter(Attendance.attendance_date <= end_date)
        
        attendance_records = query.order_by(Attendance.attendance_date.desc()).offset(skip).limit(limit).all()
        
        results = []
        for record in attendance_records:
            record_dict = {
                "attendance_id": record.attendance_id,
                "employee_id": record.employee_id,
                "attendance_date": str(record.attendance_date),
                "clock_in_time": str(record.clock_in_time) if record.clock_in_time else None,
                "clock_out_time": str(record.clock_out_time) if record.clock_out_time else None,
                "status": str(record.status),
                "hours_worked": float(record.hours_worked) if record.hours_worked else 0.0,
                "location": record.location,
                "employee_name": current_user.full_name
            }
            results.append(record_dict)
        
        return results
    
    print("DEBUG: User is admin/manager - returning ALL attendance data")
    # For admin/manager - return ALL attendance data
    query = db.query(Attendance)
    
    if start_date:
        query = query.filter(Attendance.attendance_date >= start_date)
    if end_date:
        query = query.filter(Attendance.attendance_date <= end_date)
    
    attendance_records = query.order_by(Attendance.attendance_date.desc()).offset(skip).limit(limit).all()
    print(f"DEBUG: Found {len(attendance_records)} total attendance records")
    
    results = []
    for record in attendance_records:
        employee = db.query(Employee).filter(Employee.employee_id == record.employee_id).first()
        record_dict = {
            "attendance_id": record.attendance_id,
            "employee_id": record.employee_id,
            "attendance_date": str(record.attendance_date),
            "clock_in_time": str(record.clock_in_time) if record.clock_in_time else None,
            "clock_out_time": str(record.clock_out_time) if record.clock_out_time else None,
            "status": str(record.status),
            "hours_worked": float(record.hours_worked) if record.hours_worked else 0.0,
            "location": record.location,
            "employee_name": employee.full_name if employee else "Unknown",
            "employee": {
                "employee_id": employee.employee_id,
                "full_name": employee.full_name,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "designation": employee.designation,
                "department": employee.department.department_name if employee and employee.department else None
            } if employee else None
        }
        results.append(record_dict)
    
    print(f"DEBUG: Returning {len(results)} formatted records")
    unique_employees = set(record['employee_name'] for record in results)
    print(f"DEBUG: Unique employees in results: {list(unique_employees)}")
    
    return results