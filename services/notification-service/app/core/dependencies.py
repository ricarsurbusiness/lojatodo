from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db


async def get_notification_db() -> AsyncSession:
    async for db in get_db():
        yield db
