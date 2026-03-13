from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user_model import User, user_roles
from app.models.role_model import Role
from app.core.security import get_password_hash, verify_password


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, email: str, name: str, password: str) -> User:
        password_hash = get_password_hash(password)
        user = User(
            email=email,
            name=name,
            password_hash=password_hash
        )
        self.db.add(user)
        await self.db.flush()
        
        # Get cliente role
        result = await self.db.execute(
            select(Role).where(Role.name == "cliente")
        )
        cliente_role = result.scalar_one_or_none()
        if cliente_role:
            # Use raw SQL to add role association to avoid lazy loading issues
            stmt = user_roles.insert().values(user_id=user.id, role_id=cliente_role.id)
            await self.db.execute(stmt)
        
        await self.db.commit()
        
        # Refresh with eager loading to avoid lazy loading issues
        result = await self.db.execute(
            select(User).where(User.id == user.id).options(selectinload(User.roles))
        )
        user = result.scalar_one()
        return user
    
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email).options(selectinload(User.roles))
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.id == user_id).options(selectinload(User.roles))
        )
        return result.scalar_one_or_none()
    
    async def list_users(self, page: int = 1, limit: int = 10, search: Optional[str] = None, role: Optional[str] = None) -> Tuple[List[User], int]:
        offset = (page - 1) * limit
        
        # Build base query with eager loading
        query = select(User).options(selectinload(User.roles))
        
        # Apply filters
        if search:
            query = query.where(User.email.ilike(f"%{search}%") | User.name.ilike(f"%{search}%"))
        
        # Get count
        count_query = select(func.count(User.id))
        if search:
            count_query = count_query.where(User.email.ilike(f"%{search}%") | User.name.ilike(f"%{search}%"))
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar_one()
        
        # Get paginated results
        query = query.order_by(User.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        users = list(result.scalars().all())
        
        return users, total
    
    async def update(self, user: User) -> User:
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def _get_role_by_name(self, name: str) -> Optional[Role]:
        result = await self.db.execute(
            select(Role).where(Role.name == name)
        )
        return result.scalar_one_or_none()
    
    async def assign_role(self, user: User, role_name: str) -> User:
        role = await self._get_role_by_name(role_name)
        if role and role not in user.roles:
            user.roles.append(role)
            await self.db.commit()
            await self.db.refresh(user)
        return user
    
    async def authenticate(self, email: str, password: str) -> Optional[User]:
        user = await self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
