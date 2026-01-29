from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app.models.employee import Employee
from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.dependencies import get_current_user, get_current_admin

router = APIRouter()


@router.get("/", response_model=List[DepartmentResponse])
def get_departments(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of all departments"""
    departments = db.query(Department).offset(skip).limit(limit).all()
    
    # Add employee count to each department
    result = []
    for dept in departments:
        employee_count = db.query(func.count(Employee.employee_id)).filter(
            Employee.department_id == dept.department_id,
            Employee.is_active == True
        ).scalar()
        
        dept_dict = {
            "department_id": dept.department_id,
            "department_name": dept.department_name,
            "description": dept.description,
            "created_at": dept.created_at,
            "updated_at": dept.updated_at,
            "employee_count": employee_count or 0
        }
        result.append(dept_dict)
    
    return result


@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(
    department_id: int,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get department by ID"""
    department = db.query(Department).filter(Department.department_id == department_id).first()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Get employee count
    employee_count = db.query(func.count(Employee.employee_id)).filter(
        Employee.department_id == department_id,
        Employee.is_active == True
    ).scalar()
    
    dept_dict = {
        "department_id": department.department_id,
        "department_name": department.department_name,
        "description": department.description,
        "created_at": department.created_at,
        "updated_at": department.updated_at,
        "employee_count": employee_count or 0
    }
    
    return dept_dict


@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    department: DepartmentCreate,
    current_user: Employee = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new department (Admin only)"""
    # Check if department name already exists
    existing_dept = db.query(Department).filter(
        Department.department_name == department.department_name
    ).first()
    
    if existing_dept:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department name already exists"
        )
    
    # Create department
    db_department = Department(**department.model_dump())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    
    dept_dict = {
        "department_id": db_department.department_id,
        "department_name": db_department.department_name,
        "description": db_department.description,
        "created_at": db_department.created_at,
        "updated_at": db_department.updated_at,
        "employee_count": 0
    }
    
    return dept_dict


@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(
    department_id: int,
    department_update: DepartmentUpdate,
    current_user: Employee = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update department (Admin only)"""
    department = db.query(Department).filter(Department.department_id == department_id).first()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Check if new name conflicts with existing department
    if department_update.department_name:
        existing_dept = db.query(Department).filter(
            Department.department_name == department_update.department_name,
            Department.department_id != department_id
        ).first()
        
        if existing_dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department name already exists"
            )
    
    # Update fields
    update_data = department_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(department, field, value)
    
    db.commit()
    db.refresh(department)
    
    # Get employee count
    employee_count = db.query(func.count(Employee.employee_id)).filter(
        Employee.department_id == department_id,
        Employee.is_active == True
    ).scalar()
    
    dept_dict = {
        "department_id": department.department_id,
        "department_name": department.department_name,
        "description": department.description,
        "created_at": department.created_at,
        "updated_at": department.updated_at,
        "employee_count": employee_count or 0
    }
    
    return dept_dict


@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    department_id: int,
    current_user: Employee = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete a department (Admin only)"""
    department = db.query(Department).filter(Department.department_id == department_id).first()
    
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Check if department has employees
    employee_count = db.query(func.count(Employee.employee_id)).filter(
        Employee.department_id == department_id,
        Employee.is_active == True
    ).scalar()
    
    if employee_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete department with {employee_count} active employees"
        )
    
    db.delete(department)
    db.commit()
    
    return None
