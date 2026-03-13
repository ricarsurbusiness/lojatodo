from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.category_repository import CategoryRepository
from app.models.category_model import Category


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.category_repo = CategoryRepository(db)
    
    async def create_category(self, name: str, description: Optional[str] = None, parent_id: Optional[int] = None) -> Category:
        existing = await self.category_repo.get_by_name(name)
        if existing:
            raise ValueError(f"Category with name '{name}' already exists")
        
        if parent_id:
            parent = await self.category_repo.get_by_id(parent_id)
            if not parent:
                raise ValueError("Parent category not found")
        
        return await self.category_repo.create(name, description, parent_id)
    
    async def get_category(self, category_id: int) -> Optional[Category]:
        return await self.category_repo.get_by_id(category_id)
    
    async def list_categories(self) -> List[Category]:
        return await self.category_repo.get_all()
    
    async def update_category(self, category_id: int, name: Optional[str] = None, description: Optional[str] = None) -> Optional[Category]:
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            return None
        
        if name is not None:
            existing = await self.category_repo.get_by_name(name)
            if existing and existing.id != category_id:
                raise ValueError(f"Category with name '{name}' already exists")
            category.name = name
        
        if description is not None:
            category.description = description
        
        return await self.category_repo.update(category)
    
    async def delete_category(self, category_id: int) -> bool:
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            return False
        
        await self.category_repo.delete(category)
        return True
