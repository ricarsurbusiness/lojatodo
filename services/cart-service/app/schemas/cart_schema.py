from decimal import Decimal
from typing import List
from pydantic import BaseModel, Field


class CartItemRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class CartItemUpdate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=0)


class CartItemResponse(BaseModel):
    product_id: int
    quantity: int
    name: str
    price: Decimal


class CartResponse(BaseModel):
    user_id: int
    items: List[CartItemResponse]
    total: Decimal
