from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.inventory_repository import InventoryRepository
from app.models.inventory_model import Inventory, InventoryReservation, ReservationStatus
from app.core.config import inventory_settings


class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.inventory_repo = InventoryRepository(db)
    
    async def get_inventory(self, product_id: int) -> Optional[Inventory]:
        return await self.inventory_repo.get_inventory_by_product_id(product_id)
    
    async def create_inventory(self, product_id: int, quantity: int = 0) -> Inventory:
        existing = await self.inventory_repo.get_inventory_by_product_id(product_id)
        if existing:
            # Sumar la cantidad al inventario existente
            existing.quantity += quantity
            return await self.inventory_repo.update_inventory(existing)
        return await self.inventory_repo.create_inventory(product_id, quantity)
    
    async def update_inventory_quantity(self, product_id: int, quantity: int) -> Optional[Inventory]:
        inventory = await self.inventory_repo.get_inventory_by_product_id(product_id)
        if not inventory:
            return None
        inventory.quantity = quantity
        return await self.inventory_repo.update_inventory(inventory)
    
    async def reserve_stock(
        self,
        product_id: int,
        quantity: int,
        order_id: Optional[int] = None
    ) -> tuple[Optional[InventoryReservation], Optional[str], Optional[int]]:
        inventory = await self.inventory_repo.get_inventory_with_lock(product_id)
        
        if not inventory:
            return None, "Product not found", None
        
        available = inventory.quantity - inventory.reserved_quantity
        
        if available < quantity:
            return None, "Insufficient stock", available
        
        ttl_minutes = inventory_settings.RESERVATION_TTL_MINUTES
        expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)
        
        reservation = await self.inventory_repo.create_reservation(
            product_id=product_id,
            quantity=quantity,
            expires_at=expires_at,
            order_id=order_id
        )
        
        inventory.reserved_quantity += quantity
        await self.inventory_repo.update_inventory(inventory)
        
        return reservation, None, None
    
    async def confirm_reservation(self, reservation_id: int) -> tuple[Optional[InventoryReservation], str]:
        reservation = await self.inventory_repo.get_reservation_with_lock(reservation_id)
        
        if not reservation:
            return None, "Reservation not found"
        
        if reservation.status == ReservationStatus.CONFIRMED:
            return reservation, "Reservation already confirmed"
        
        if reservation.status == ReservationStatus.RELEASED:
            return None, "Reservation already released"
        
        if reservation.status == ReservationStatus.EXPIRED or reservation.expires_at < datetime.utcnow():
            return None, "Reservation has expired"
        
        reservation.status = ReservationStatus.CONFIRMED
        await self.inventory_repo.update_reservation(reservation)
        
        return reservation, "Success"
    
    async def release_reservation(self, reservation_id: int) -> tuple[Optional[InventoryReservation], str]:
        reservation = await self.inventory_repo.get_reservation_with_lock(reservation_id)
        
        if not reservation:
            return None, "Reservation not found"
        
        if reservation.status == ReservationStatus.CONFIRMED:
            return None, "Cannot release confirmed reservation"
        
        if reservation.status == ReservationStatus.RELEASED:
            return reservation, "Reservation already released"
        
        if reservation.status == ReservationStatus.EXPIRED:
            return None, "Reservation already expired"
        
        inventory = await self.inventory_repo.get_inventory_with_lock(reservation.product_id)
        
        if inventory:
            inventory.reserved_quantity -= reservation.quantity
            await self.inventory_repo.update_inventory(inventory)
        
        reservation.status = ReservationStatus.RELEASED
        await self.inventory_repo.update_reservation(reservation)
        
        return reservation, "Success"
    
    async def cleanup_expired_reservations(self) -> int:
        expired_reservations = await self.inventory_repo.get_expired_reservations()
        
        for reservation in expired_reservations:
            inventory = await self.inventory_repo.get_inventory_with_lock(reservation.product_id)
            
            if inventory:
                inventory.reserved_quantity -= reservation.quantity
                if inventory.reserved_quantity < 0:
                    inventory.reserved_quantity = 0
                await self.inventory_repo.update_inventory(inventory)
            
            reservation.status = ReservationStatus.EXPIRED
            await self.inventory_repo.update_reservation(reservation)
        
        return len(expired_reservations)
