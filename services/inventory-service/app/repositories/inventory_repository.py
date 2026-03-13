from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory_model import Inventory, InventoryReservation, ReservationStatus


class InventoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_inventory_by_product_id(self, product_id: int) -> Optional[Inventory]:
        result = await self.db.execute(
            select(Inventory).where(Inventory.product_id == product_id)
        )
        return result.scalar_one_or_none()
    
    async def get_inventory_with_lock(self, product_id: int) -> Optional[Inventory]:
        result = await self.db.execute(
            select(Inventory)
            .where(Inventory.product_id == product_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()
    
    async def create_inventory(self, product_id: int, quantity: int = 0) -> Inventory:
        inventory = Inventory(
            product_id=product_id,
            quantity=quantity,
            reserved_quantity=0
        )
        self.db.add(inventory)
        await self.db.commit()
        await self.db.refresh(inventory)
        return inventory
    
    async def update_inventory(self, inventory: Inventory) -> Inventory:
        await self.db.commit()
        await self.db.refresh(inventory)
        return inventory
    
    async def get_reservation_by_id(self, reservation_id: int) -> Optional[InventoryReservation]:
        result = await self.db.execute(
            select(InventoryReservation).where(InventoryReservation.reservation_id == reservation_id)
        )
        return result.scalar_one_or_none()
    
    async def get_reservation_with_lock(self, reservation_id: int) -> Optional[InventoryReservation]:
        result = await self.db.execute(
            select(InventoryReservation)
            .where(InventoryReservation.reservation_id == reservation_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()
    
    async def create_reservation(
        self,
        product_id: int,
        quantity: int,
        expires_at: datetime,
        order_id: Optional[int] = None
    ) -> InventoryReservation:
        reservation = InventoryReservation(
            product_id=product_id,
            quantity=quantity,
            expires_at=expires_at,
            status=ReservationStatus.PENDING,
            order_id=order_id
        )
        self.db.add(reservation)
        await self.db.commit()
        await self.db.refresh(reservation)
        return reservation
    
    async def update_reservation(self, reservation: InventoryReservation) -> InventoryReservation:
        await self.db.commit()
        await self.db.refresh(reservation)
        return reservation
    
    async def get_expired_reservations(self) -> List[InventoryReservation]:
        result = await self.db.execute(
            select(InventoryReservation)
            .where(InventoryReservation.status == ReservationStatus.PENDING)
            .where(InventoryReservation.expires_at < datetime.utcnow())
        )
        return list(result.scalars().all())
    
    async def get_active_reservations_for_product(self, product_id: int) -> List[InventoryReservation]:
        result = await self.db.execute(
            select(InventoryReservation)
            .where(InventoryReservation.product_id == product_id)
            .where(InventoryReservation.status == ReservationStatus.PENDING)
            .where(InventoryReservation.expires_at > datetime.utcnow())
        )
        return list(result.scalars().all())
