# dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employee import Employee, UserRole
from app.utils.security import decode_token

security = HTTPBearer()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Employee:
    """
    Get the currently logged-in user from the JWT token.
    """
    token = credentials.credentials  # Extract Bearer token

    try:
        payload = decode_token(token)
        print("Decoded JWT token:", payload)

        user_id_str = payload.get("sub")
        role_str = payload.get("role")
        token_type = payload.get("type")

        if not user_id_str or not role_str or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user_id",
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

    except HTTPException:
        raise  # Re-raise HTTPExceptions as-is
    except Exception as e:
        print(f"Token decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(Employee).filter(Employee.employee_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate employee",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Convert role string to enum
    try:
        # The role in token is already the enum name (e.g., "ADMIN")
        # We need to convert it to the enum value
        user_role = UserRole(role_str)
        user.role = user_role
        print(f"Role conversion successful: {role_str} -> {user_role}")
    except ValueError as e:
        print(f"Role conversion failed: {role_str} -> {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid role in token: {role_str}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_admin(
    current_user: Employee = Depends(get_current_user)
) -> Employee:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


def get_current_manager_or_admin(
    current_user: Employee = Depends(get_current_user)
) -> Employee:
    if current_user.role not in (UserRole.ADMIN, UserRole.MANAGER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or Admin privileges required",
        )
    return current_user
