import httpx
from typing import Optional
from decimal import Decimal
from fastapi import HTTPException, status

from app.core.config import cart_settings


class ProductInfo:
    def __init__(self, product_id: int, name: str, price: Decimal, stock: int):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock


async def validate_product_exists(product_id: int) -> ProductInfo:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{cart_settings.PRODUCT_SERVICE_URL}/api/v1/products/{product_id}",
                timeout=5.0
            )
            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found"
                )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_503_UNAVAILABLE,
                    detail="Product service unavailable"
                )
            product_data = response.json()
            return ProductInfo(
                product_id=product_data["id"],
                name=product_data["name"],
                price=Decimal(str(product_data["price"])),
                stock=product_data.get("stock", 0)
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_UNAVAILABLE,
                detail="Product service unavailable"
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_503_UNAVAILABLE,
                detail="Product service timeout"
            )


async def get_product_price(product_id: int) -> Optional[Decimal]:
    product = await validate_product_exists(product_id)
    return product.price
