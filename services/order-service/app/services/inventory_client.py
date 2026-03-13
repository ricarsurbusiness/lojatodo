from typing import Dict, Any, Optional
import httpx

from app.core.config import order_settings


class InventoryClient:
    async def reserve(self, product_id: int, quantity: int, order_id: int, token: Optional[str] = None) -> Dict[str, Any]:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{order_settings.INVENTORY_SERVICE_URL}/api/v1/inventory/reserve",
                json={
                    "product_id": product_id,
                    "quantity": quantity,
                    "order_id": order_id,
                },
                headers=headers,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def confirm(self, reservation_id: int, token: Optional[str] = None) -> Dict[str, Any]:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{order_settings.INVENTORY_SERVICE_URL}/api/v1/inventory/confirm",
                json={"reservation_id": reservation_id},
                headers=headers,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def release(self, reservation_id: int, token: Optional[str] = None) -> Dict[str, Any]:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{order_settings.INVENTORY_SERVICE_URL}/api/v1/inventory/release",
                json={"reservation_id": reservation_id},
                headers=headers,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()
