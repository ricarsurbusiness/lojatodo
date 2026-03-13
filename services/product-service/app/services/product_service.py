from typing import Optional, List
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.product_repository import ProductRepository
from app.models.product_model import Product


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.product_repo = ProductRepository(db)
    
    async def create_product(self, name: str, description: Optional[str], price: Decimal, category_id: Optional[int] = None) -> Product:
        return await self.product_repo.create(name, description, float(price), category_id)
    
    async def get_product(self, product_id: int) -> Optional[Product]:
        return await self.product_repo.get_by_id(product_id)
    
    async def list_products(self, skip: int = 0, limit: int = 20, search: Optional[str] = None) -> List[Product]:
        return await self.product_repo.get_all(skip, limit, search)
    
    async def count_products(self, search: Optional[str] = None) -> int:
        return await self.product_repo.count(search)
    
    async def update_product(self, product_id: int, name: Optional[str] = None, description: Optional[str] = None, price: Optional[Decimal] = None, category_id: Optional[int] = None) -> Optional[Product]:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            return None
        
        if name is not None:
            product.name = name
        if description is not None:
            product.description = description
        if price is not None:
            product.price = float(price)
        if category_id is not None:
            product.category_id = category_id
        
        return await self.product_repo.update(product)
    
    async def delete_product(self, product_id: int) -> bool:
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            return False
        
        await self.product_repo.delete(product)
        return True
