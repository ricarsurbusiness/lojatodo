from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.models.user_model import User
from app.core.dependencies import CurrentUser


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def get_current_user(self, user_id: int) -> Optional[User]:
        return await self.user_repo.get_by_id(user_id)
    
    async def update_profile(self, user: User, name: Optional[str] = None) -> User:
        if name:
            user.name = name
        return await self.user_repo.update(user)
    
    async def list_users(self, page: int = 1, limit: int = 10, search: Optional[str] = None, role: Optional[str] = None) -> Tuple[List[User], int]:
        return await self.user_repo.list_users(page=page, limit=limit, search=search, role=role)
    
    async def assign_role(self, target_user_id: int, role_name: str, current_user: CurrentUser) -> User:
        if "admin" in current_user.roles and role_name == "admin":
            raise ValueError("Only superAdmin can assign admin role")
        
        if role_name not in ["admin", "cliente"]:
            raise ValueError("Invalid role")
        
        target_user = await self.user_repo.get_by_id(target_user_id)
        if not target_user:
            raise ValueError("User not found")
        
        return await self.user_repo.assign_role(target_user, role_name)
