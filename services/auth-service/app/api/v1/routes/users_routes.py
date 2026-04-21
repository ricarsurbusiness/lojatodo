from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user_schema import UserResponse, UserUpdate, AssignRoleRequest
from app.services.user_service import UserService
from app.core.dependencies import get_current_user, CurrentUser, require_role

router = APIRouter(prefix="", tags=["users"])


@router.get("/users")
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(require_role(["admin", "superAdmin"])),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    users, total = await user_service.list_users(page=page, limit=limit, search=search, role=role)
    
    pages = (total + limit - 1) // limit
    
    return {
        "items": [
            UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                roles=[r.name for r in user.roles],
                created_at=user.created_at
            )
            for user in users
        ],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    user = await user_service.get_current_user(current_user.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        roles=[role.name for role in user.roles],
        created_at=user.created_at
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: UserUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    user = await user_service.get_current_user(current_user.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = await user_service.update_profile(user, request.name)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        roles=[role.name for role in user.roles],
        created_at=user.created_at
    )


@router.post("/assign-role", response_model=UserResponse)
async def assign_role(
    request: AssignRoleRequest,
    current_user: CurrentUser = Depends(require_role(["admin", "superAdmin"])),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    try:
        user = await user_service.assign_role(request.user_id, request.role, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        roles=[role.name for role in user.roles],
        created_at=user.created_at
    )


@router.post("/remove-role", response_model=UserResponse)
async def remove_role(
    request: AssignRoleRequest,
    current_user: CurrentUser = Depends(require_role(["admin", "superAdmin"])),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    try:
        user = await user_service.remove_role(request.user_id, request.role, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        roles=[role.name for role in user.roles],
        created_at=user.created_at
    )


@router.delete("/users/{user_id}/roles/{role_name}")
async def remove_role(
    user_id: int,
    role_name: str,
    current_user: CurrentUser = Depends(require_role(["admin", "superAdmin"])),
    db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    try:
        user = await user_service.remove_role(user_id, role_name, current_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        roles=[role.name for role in user.roles],
        created_at=user.created_at
    )
