from typing import AsyncGenerator, List, Optional
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
import httpx

from app.core.config import analytics_settings
from app.db.session import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

_redis_client: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(analytics_settings.REDIS_URL, decode_responses=True)
    return _redis_client


async def close_redis():
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, analytics_settings.JWT_SECRET_KEY, algorithm=analytics_settings.JWT_ALGORITHM)
    return encoded_jwt


class CurrentUser:
    def __init__(self, user_id: int, email: str, roles: List[str]):
        self.user_id = user_id
        self.email = email
        self.roles = roles


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> CurrentUser:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{analytics_settings.AUTH_SERVICE_URL}/api/v1/auth/verify",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                )
            user_data = response.json()
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_UNAVAILABLE,
                detail="Auth service unavailable",
            )
    
    return CurrentUser(
        user_id=user_data.get("user_id"),
        email=user_data.get("email"),
        roles=user_data.get("roles", [])
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
