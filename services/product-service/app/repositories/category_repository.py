from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category_model import Category


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, name: str, description: Optional[str] = None, parent_id: Optional[int] = None) -> Category:
        category = Category(
            name=name,
            description=description,
            parent_id=parent_id
        )
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category
    
    async def get_by_id(self, category_id: int) -> Optional[Category]:
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[Category]:
        result = await self.db.execute(
            select(Category).where(Category.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[Category]:
        result = await self.db.execute(select(Category))
        return list(result.scalars().all())
    
    async def update(self, category: Category) -> Category:
        await self.db.commit()
        await self.db.refresh(category)
        return category
    
    async def delete(self, category: Category) -> None:
        await self.db.delete(category)
        await self.db.commit()
