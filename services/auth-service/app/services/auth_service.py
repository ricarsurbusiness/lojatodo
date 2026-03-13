from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.models.user_model import User
from app.core.dependencies import create_access_token, create_refresh_token
from app.core.config import auth_settings
from app.schemas.token_schema import TokenResponse


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def register(self, email: str, name: str, password: str) -> User:
        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")
        
        user = await self.user_repo.create(email, name, password)
        return user
    
    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.user_repo.authenticate(email, password)
        if not user:
            raise ValueError("Invalid credentials")
        
        access_token = self._create_token(user)
        refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )
    
    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        from app.core.dependencies import verify_token
        from jose import jwt, JWTError
        
        try:
            payload = jwt.decode(
                refresh_token, 
                auth_settings.JWT_SECRET_KEY, 
                algorithms=[auth_settings.JWT_ALGORITHM]
            )
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")
            
            user_id = payload.get("sub")
            user = await self.user_repo.get_by_id(int(user_id))
            if not user:
                raise ValueError("User not found")
            
            new_access_token = self._create_token(user)
            new_refresh_token = create_refresh_token({"sub": str(user.id), "email": user.email})
            
            return TokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token
            )
        except JWTError:
            raise ValueError("Invalid refresh token")
    
    def _create_token(self, user: User) -> str:
        roles = [role.name for role in user.roles]
        return create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "roles": roles
            }
        )
