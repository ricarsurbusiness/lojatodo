from typing import List
from fastapi import Depends, HTTPException, status

from app.core.dependencies import CurrentUser, get_current_user


ADMIN_ROLES = ["superAdmin", "admin"]


async def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if not any(role in current_user.roles for role in ADMIN_ROLES):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def check_permission(user: CurrentUser, required_roles: List[str]) -> bool:
    return any(role in user.roles for role in required_roles)
