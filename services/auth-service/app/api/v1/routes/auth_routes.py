from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user_schema import UserRegisterRequest, UserResponse, UserUpdate, AssignRoleRequest
from app.schemas.token_schema import LoginRequest, TokenResponse, RefreshTokenRequest
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.core.dependencies import get_current_user, CurrentUser

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    try:
        user = await auth_service.register(request.email, request.name, request.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        roles=[role.name for role in user.roles],
        created_at=user.created_at
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    try:
        tokens = await auth_service.login(request.email, request.password)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)
    try:
        tokens = await auth_service.refresh_access_token(request.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    return tokens


class TokenVerifyResponse(BaseModel):
    user_id: int
    email: str
    roles: List[str]


@router.get("/verify", response_model=TokenVerifyResponse)
async def verify_token(
    current_user: CurrentUser = Depends(get_current_user)
):
    return TokenVerifyResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        roles=current_user.roles
    )
