from typing import List, Optional
from datetime import datetime
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer

from app.core.config import admin_settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class CurrentUser:
    def __init__(self, user_id: int, email: str, roles: List[str], token: Optional[str] = None):
        self.user_id = user_id
        self.email = email
        self.roles = roles
        self.token = token


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, admin_settings.JWT_SECRET_KEY, algorithms=[admin_settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    payload = verify_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    roles = payload.get("roles", [])
    
    return CurrentUser(
        user_id=int(user_id),
        email=payload.get("email", ""),
        roles=roles,
        token=token
    )


def require_role(allowed_roles: List[str]):
    async def role_checker(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if not any(role in current_user.roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


def require_admin(current_user: CurrentUser = Depends(require_role(["admin", "superAdmin"]))) -> CurrentUser:
    return current_user
