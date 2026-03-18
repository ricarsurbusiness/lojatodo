import httpx
from fastapi import HTTPException, status

from app.core.config import cart_settings


class InventoryInfo:
    def __init__(self, product_id: int, quantity: int, reserved_quantity: int, available_quantity: int):
        self.product_id = product_id
        self.quantity = quantity
        self.reserved_quantity = reserved_quantity
        self.available_quantity = available_quantity


async def validate_inventory_available(product_id: int, quantity: int) -> InventoryInfo:
    """
    Check if product has available inventory for the requested quantity.
    Raises HTTPException if insufficient stock.
    """
    # First get product name for error messages
    product_name = None
    async with httpx.AsyncClient() as client:
        try:
            product_response = await client.get(
                f"{cart_settings.PRODUCT_SERVICE_URL}/api/v1/products/{product_id}",
                timeout=5.0
            )
            if product_response.status_code == 200:
                product_data = product_response.json()
                product_name = product_data.get("name", f"Producto {product_id}")
            elif product_response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Producto no encontrado"
                )
        except httpx.RequestError:
            pass
    
    product_display = product_name or f"Producto {product_id}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{cart_settings.INVENTORY_SERVICE_URL}/api/v1/inventory/{product_id}",
                timeout=5.0
            )
            
            # If inventory doesn't exist, product is not available
            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"'{product_display}' no está disponible"
                )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_503_UNAVAILABLE,
                    detail="Servicio de inventario no disponible"
                )
            
            inventory_data = response.json()
            available = inventory_data.get("available_quantity", 0)
            
            if available < quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuficiente para '{product_display}'. Disponible: {available}, solicitado: {quantity}"
                )
            
            return InventoryInfo(
                product_id=inventory_data["product_id"],
                quantity=inventory_data["quantity"],
                reserved_quantity=inventory_data["reserved_quantity"],
                available_quantity=available
            )
            
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_UNAVAILABLE,
                detail="Servicio de inventario no disponible"
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_503_UNAVAILABLE,
                detail="Tiempo de espera del servicio de inventario agotado"
            )
