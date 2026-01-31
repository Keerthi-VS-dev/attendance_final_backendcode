from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional
from app.database import get_db
from app.models.employee import Employee, UserRole
from app.models.department import Department
from app.models.rave import Rave
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeDetail
)
from app.utils.security import get_password_hash
from app.dependencies import get_current_user, get_current_admin

router = APIRouter()


@router.get("/", response_model=List[EmployeeResponse])
def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),  # Increased default and max limit
    department_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of all employees with optional filters"""
    from sqlalchemy.orm import joinedload
    
    query = db.query(Employee).options(joinedload(Employee.department))
    
    # Apply filters
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    
    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Employee.first_name.ilike(search_filter),
                Employee.last_name.ilike(search_filter),
                Employee.email.ilike(search_filter),
                Employee.designation.ilike(search_filter)
            )
        )
    
    employees = query.offset(skip).limit(limit).all()
    return employees


@router.get("/{employee_id}", response_model=EmployeeDetail)
def get_employee(
    employee_id: int,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get employee details by ID"""
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Get department name
    department_name = None
    if employee.department_id:
        department = db.query(Department).filter(
            Department.department_id == employee.department_id
        ).first()
        if department:
            department_name = department.department_name
    
    # Get manager name
    manager_name = None
    if employee.manager_id:
        manager = db.query(Employee).filter(
            Employee.employee_id == employee.manager_id
        ).first()
        if manager:
            manager_name = manager.full_name
    
    # Get rave count
    rave_count = db.query(func.count(Rave.rave_id)).filter(
        Rave.to_employee_id == employee_id
    ).scalar()
    
    # Create response
    employee_dict = {
        "employee_id": employee.employee_id,
        "email": employee.email,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "phone": employee.phone,
        "date_of_birth": employee.date_of_birth,
        "joining_date": employee.joining_date,
        "designation": employee.designation,
        "department_id": employee.department_id,
        "manager_id": employee.manager_id,
        "role": employee.role,
        "profile_picture_url": employee.profile_picture_url,
        "is_active": employee.is_active,
        "created_at": employee.created_at,
        "updated_at": employee.updated_at,
        "department_name": department_name,
        "manager_name": manager_name,
        "rave_count": rave_count or 0
    }
    
    return employee_dict


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee: EmployeeCreate,
    current_user: Employee = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new employee (Admin only)"""
    # Check if email already exists
    existing_employee = db.query(Employee).filter(Employee.email == employee.email).first()
    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verify department exists if provided
    if employee.department_id:
        department = db.query(Department).filter(
            Department.department_id == employee.department_id
        ).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
    
    # Verify manager exists if provided
    if employee.manager_id:
        manager = db.query(Employee).filter(
            Employee.employee_id == employee.manager_id
        ).first()
        if not manager:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Manager not found"
            )
    
    # Create new employee
    db_employee = Employee(
        email=employee.email,
        password_hash=get_password_hash(employee.password),
        first_name=employee.first_name,
        last_name=employee.last_name,
        phone=employee.phone,
        date_of_birth=employee.date_of_birth,
        joining_date=employee.joining_date,
        designation=employee.designation,
        department_id=employee.department_id,
        manager_id=employee.manager_id,
        role=employee.role
    )
    
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    
    return db_employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    employee_update: EmployeeUpdate,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update employee information"""
    # Get employee
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Check permissions: user can update themselves, or admin can update anyone
    if current_user.role != UserRole.ADMIN and current_user.employee_id != employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Only admin can change role and is_active
    if current_user.role != UserRole.ADMIN:
        employee_update.role = None
        employee_update.is_active = None
    
    # Update fields
    update_data = employee_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)
    
    db.commit()
    db.refresh(employee)
    
    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: int,
    current_user: Employee = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete an employee (Admin only - soft delete)"""
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Soft delete
    employee.is_active = False
    db.commit()
    
    return None


@router.get("/{employee_id}/subordinates", response_model=List[EmployeeResponse])
def get_subordinates(
    employee_id: int,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all subordinates of an employee"""
    # Check if employee exists
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Get subordinates
    subordinates = db.query(Employee).filter(Employee.manager_id == employee_id).all()
    
    return subordinates
