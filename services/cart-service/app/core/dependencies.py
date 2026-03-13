from typing import List
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import redis.asyncio as redis

from app.core.config import cart_settings
from app.db.redis_client import get_redis_client


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class CurrentUser:
    def __init__(self, user_id: int, email: str, roles: List[str]):
        self.user_id = user_id
        self.email = email
        self.roles = roles


async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{cart_settings.AUTH_SERVICE_URL}/api/v1/auth/verify",
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


async def get_redis() -> redis.Redis:
    return await get_redis_client()
