from datetime import date, datetime, time as dt_time
from typing import Optional
from sqlalchemy.orm import Session
from app.models.attendance import Attendance, AttendanceStatus
from app.models.employee import Employee
from app.config import settings


class AttendanceService:
    """Service class for attendance-related business logic"""
    
    @staticmethod
    def calculate_hours_worked(clock_in: dt_time, clock_out: dt_time) -> float:
        """Calculate hours worked between clock in and clock out times"""
        if not clock_in or not clock_out:
            return 0.0
        
        # Convert times to datetime for calculation
        today = date.today()
        dt_in = datetime.combine(today, clock_in)
        dt_out = datetime.combine(today, clock_out)
        
        # Handle overnight shifts
        if dt_out < dt_in:
            dt_out = dt_out.replace(day=dt_out.day + 1)
        
        # Calculate difference
        diff = dt_out - dt_in
        hours = diff.total_seconds() / 3600
        
        return round(hours, 2)
    
    @staticmethod
    def determine_attendance_status(clock_in: dt_time, clock_out: Optional[dt_time] = None) -> AttendanceStatus:
        """Determine attendance status based on clock in time"""
        if not clock_in:
            return AttendanceStatus.ABSENT
        
        # Parse work start time from settings
        work_start = datetime.strptime(settings.WORK_START_TIME, "%H:%M").time()
        
        # Calculate late threshold
        late_threshold = datetime.combine(date.today(), work_start)
        from datetime import timedelta
        late_threshold = (late_threshold + 
                         timedelta(minutes=settings.LATE_ARRIVAL_THRESHOLD_MINUTES)).time()
        
        if clock_in > late_threshold:
            return AttendanceStatus.LATE
        
        return AttendanceStatus.PRESENT
    
    @staticmethod
    def get_today_attendance(db: Session, employee_id: int) -> Optional[Attendance]:
        """Get today's attendance record for an employee"""
        today = date.today()
        return db.query(Attendance).filter(
            Attendance.employee_id == employee_id,
            Attendance.attendance_date == today
        ).first()
    
    @staticmethod
    def can_clock_in(db: Session, employee_id: int) -> tuple[bool, str]:
        """Check if employee can clock in"""
        attendance = AttendanceService.get_today_attendance(db, employee_id)
        
        if attendance and attendance.clock_in_time:
            return False, "Already clocked in today"
        
        return True, "Can clock in"
    
    @staticmethod
    def can_clock_out(db: Session, employee_id: int) -> tuple[bool, str]:
        """Check if employee can clock out"""
        attendance = AttendanceService.get_today_attendance(db, employee_id)
        
        if not attendance:
            return False, "No clock-in record found for today"
        
        if not attendance.clock_in_time:
            return False, "Must clock in before clocking out"
        
        if attendance.clock_out_time:
            return False, "Already clocked out today"
        
        return True, "Can clock out"