from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.employee import Employee
from app.schemas.employee import Token, EmployeeLogin, ChangePassword, EmployeeResponse
from app.utils.security import verify_password, create_access_token, create_refresh_token, get_password_hash, decode_token
from app.dependencies import get_current_user
from datetime import timedelta
from app.config import settings

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint for user authentication"""
    # Find user by email
    employee = db.query(Employee).filter(Employee.email == form_data.username).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(form_data.password, employee.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": str(employee.employee_id),  # Convert to string for JWT compliance
            "email": employee.email,
            "role": employee.role.value  # Use .value (e.g., "admin") instead of .name (e.g., "ADMIN")
        }
    )

    # Create refresh token
    refresh_token = create_refresh_token(
        data={"sub": str(employee.employee_id), "email": employee.email}  # Convert to string
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=EmployeeResponse)
def get_current_user_info(
    current_user: Employee = Depends(get_current_user)
):
    """Get current user information"""
    return current_user


@router.post("/change-password")
def change_password(
    password_data: ChangePassword,
    current_user: Employee = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    try:
        payload = decode_token(refresh_token)
        token_type = payload.get("type")
        
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id_str = payload.get("sub")
        email = payload.get("email")
        
        if not user_id_str or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Convert string user_id back to integer
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify user still exists and is active
        employee = db.query(Employee).filter(Employee.employee_id == user_id).first()
        if not employee or not employee.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new tokens
        new_access_token = create_access_token(
            data={
                "sub": str(employee.employee_id),  # Convert to string
                "email": employee.email,
                "role": employee.role.value  # Use .value instead of .name
            }
        )
        
        new_refresh_token = create_refresh_token(
            data={"sub": str(employee.employee_id), "email": employee.email}  # Convert to string
        )
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
def logout(current_user: Employee = Depends(get_current_user)):
    """Logout endpoint (client should discard token)"""
    return {"message": "Successfully logged out"}
