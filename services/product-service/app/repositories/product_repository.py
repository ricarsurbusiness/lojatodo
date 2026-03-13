from typing import Optional, List
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product_model import Product


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, name: str, description: Optional[str], price: float, category_id: Optional[int] = None) -> Product:
        product = Product(
            name=name,
            description=description,
            price=price,
            category_id=category_id
        )
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product
    
    async def get_by_id(self, product_id: int) -> Optional[Product]:
        result = await self.db.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 20, search: Optional[str] = None) -> List[Product]:
        query = select(Product)
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count(self, search: Optional[str] = None) -> int:
        query = select(func.count(Product.id))
        
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )
        
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def update(self, product: Product) -> Product:
        await self.db.commit()
        await self.db.refresh(product)
        return product
    
    async def delete(self, product: Product) -> None:
        await self.db.delete(product)
        await self.db.commit()
