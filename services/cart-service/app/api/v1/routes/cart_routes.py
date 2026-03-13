from fastapi import APIRouter, Depends, status
import redis.asyncio as redis

from app.core.dependencies import CurrentUser, get_current_user, get_redis
from app.schemas.cart_schema import (
    CartResponse, 
    CartItemRequest, 
    CartItemUpdate
)
from app.services.cart_service import CartService

router = APIRouter(prefix="/cart", tags=["cart"])


def get_cart_service(redis_client: redis.Redis = Depends(get_redis)) -> CartService:
    return CartService(redis_client)


@router.get("", response_model=CartResponse)
async def get_cart(
    current_user: CurrentUser = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    return await cart_service.get_cart(current_user.user_id)


@router.post("/add", response_model=CartResponse)
async def add_to_cart(
    item: CartItemRequest,
    current_user: CurrentUser = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    return await cart_service.add_item(
        current_user.user_id, 
        item.product_id, 
        item.quantity
    )


@router.post("/update", response_model=CartResponse)
async def update_cart_item(
    item: CartItemUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    return await cart_service.update_item(
        current_user.user_id,
        item.product_id,
        item.quantity
    )


@router.post("/remove", response_model=CartResponse)
async def remove_from_cart(
    product_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    cart_service: CartService = Depends(get_cart_service)
):
    return await cart_service.remove_item(current_user.user_id, product_id)
