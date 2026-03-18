import json
from decimal import Decimal
from typing import List, Dict, Any
import redis.asyncio as redis
from fastapi import HTTPException, status

from app.schemas.cart_schema import CartItemResponse, CartResponse
from app.services.product_client import validate_product_exists
from app.services.inventory_client import validate_inventory_available


CART_KEY_PREFIX = "cart:"


def get_cart_key(user_id: int) -> str:
    return f"{CART_KEY_PREFIX}{user_id}"


class CartService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def get_cart(self, user_id: int) -> CartResponse:
        cart_key = get_cart_key(user_id)
        cart_data = await self.redis.hgetall(cart_key)
        
        items: List[CartItemResponse] = []
        total = Decimal("0")
        
        for product_id, item_json in cart_data.items():
            item = json.loads(item_json)
            item_response = CartItemResponse(
                product_id=int(product_id),
                quantity=item["quantity"],
                name=item["name"],
                price=Decimal(str(item["price"]))
            )
            items.append(item_response)
            total += item_response.price * item_response.quantity
        
        return CartResponse(
            user_id=user_id,
            items=items,
            total=total
        )

    async def add_item(self, user_id: int, product_id: int, quantity: int) -> CartResponse:
        # Validate product exists
        product = await validate_product_exists(product_id)
        
        cart_key = get_cart_key(user_id)
        existing_item = await self.redis.hget(cart_key, str(product_id))
        
        # Calculate current quantity in cart
        current_quantity = 0
        if existing_item:
            item_data = json.loads(existing_item)
            current_quantity = item_data["quantity"]
        
        # Calculate new total quantity
        new_total_quantity = current_quantity + quantity
        
        # Validate against available inventory (considering current cart quantity)
        inventory_info = await validate_inventory_available(product_id, new_total_quantity)
        
        if existing_item:
            item_data = json.loads(existing_item)
            item_data["quantity"] = new_total_quantity
            await self.redis.hset(
                cart_key, 
                str(product_id), 
                json.dumps(item_data)
            )
        else:
            item_data = {
                "product_id": product_id,
                "name": product.name,
                "price": str(product.price),
                "quantity": quantity
            }
            await self.redis.hset(
                cart_key,
                str(product_id),
                json.dumps(item_data)
            )
        
        return await self.get_cart(user_id)

    async def update_item(self, user_id: int, product_id: int, quantity: int) -> CartResponse:
        cart_key = get_cart_key(user_id)
        
        if quantity == 0:
            return await self.remove_item(user_id, product_id)
        
        existing_item = await self.redis.hget(cart_key, str(product_id))
        if not existing_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado en el carrito"
            )
        
        product = await validate_product_exists(product_id)
        
        item_data = {
            "product_id": product_id,
            "name": product.name,
            "price": str(product.price),
            "quantity": quantity
        }
        
        await self.redis.hset(cart_key, str(product_id), json.dumps(item_data))
        
        return await self.get_cart(user_id)

    async def decrease_item(self, user_id: int, product_id: int) -> CartResponse:
        """Decrease item quantity by 1. Remove item if quantity reaches 0."""
        cart_key = get_cart_key(user_id)
        
        existing_item = await self.redis.hget(cart_key, str(product_id))
        if not existing_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado en el carrito"
            )
        
        item_data = json.loads(existing_item)
        current_quantity = item_data["quantity"]
        
        if current_quantity <= 1:
            # Remove completely if quantity is 1 or less
            await self.redis.hdel(cart_key, str(product_id))
        else:
            # Decrease by 1
            item_data["quantity"] = current_quantity - 1
            await self.redis.hset(cart_key, str(product_id), json.dumps(item_data))
        
        return await self.get_cart(user_id)

    async def remove_item(self, user_id: int, product_id: int) -> CartResponse:
        cart_key = get_cart_key(user_id)
        await self.redis.hdel(cart_key, str(product_id))
        
        return await self.get_cart(user_id)

    async def clear_cart(self, user_id: int) -> None:
        cart_key = get_cart_key(user_id)
        await self.redis.delete(cart_key)
