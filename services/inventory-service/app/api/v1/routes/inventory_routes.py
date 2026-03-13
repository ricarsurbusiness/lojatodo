from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.inventory_schema import (
    InventoryResponse,
    InventoryCreate,
    ReserveRequest,
    ReserveResponse,
    ConfirmRequest,
    ConfirmResponse,
    ReleaseRequest,
    ReleaseResponse,
    ErrorResponse
)
from app.services.inventory_service import InventoryService
from app.core.dependencies import get_current_user, CurrentUser

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/{product_id}", response_model=InventoryResponse)
async def get_inventory(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    inventory_service = InventoryService(db)
    inventory = await inventory_service.get_inventory(product_id)
    
    if not inventory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found for this product"
        )
    
    return InventoryResponse(
        product_id=inventory.product_id,
        quantity=inventory.quantity,
        reserved_quantity=inventory.reserved_quantity,
        available_quantity=inventory.available_quantity
    )


@router.post("", response_model=InventoryResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory(
    request: InventoryCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    inventory_service = InventoryService(db)
    inventory = await inventory_service.create_inventory(
        product_id=request.product_id,
        quantity=request.quantity
    )
    
    return InventoryResponse(
        product_id=inventory.product_id,
        quantity=inventory.quantity,
        reserved_quantity=inventory.reserved_quantity,
        available_quantity=inventory.available_quantity
    )


@router.post("/reserve", response_model=ReserveResponse, responses={409: {"model": ErrorResponse}})
async def reserve_stock(
    request: ReserveRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    inventory_service = InventoryService(db)
    
    reservation, error, available = await inventory_service.reserve_stock(
        product_id=request.product_id,
        quantity=request.quantity,
        order_id=request.order_id
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "detail": error,
                "available_quantity": available
            }
        )
    
    return ReserveResponse(
        reservation_id=reservation.reservation_id,
        product_id=reservation.product_id,
        quantity=reservation.quantity,
        expires_at=reservation.expires_at
    )


@router.post("/confirm", response_model=ConfirmResponse)
async def confirm_reservation(
    request: ConfirmRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    inventory_service = InventoryService(db)
    
    reservation, message = await inventory_service.confirm_reservation(request.reservation_id)
    
    if not reservation:
        if "expired" in message.lower():
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail=message
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return ConfirmResponse(
        reservation_id=reservation.reservation_id,
        status=reservation.status.value,
        message=message
    )


@router.post("/release", response_model=ReleaseResponse)
async def release_reservation(
    request: ReleaseRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    inventory_service = InventoryService(db)
    
    reservation, message = await inventory_service.release_reservation(request.reservation_id)
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return ReleaseResponse(
        reservation_id=reservation.reservation_id,
        status=reservation.status.value,
        message=message
    )


@router.post("/cleanup", status_code=status.HTTP_200_OK)
async def cleanup_expired_reservations(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    inventory_service = InventoryService(db)
    cleaned = await inventory_service.cleanup_expired_reservations()
    
    return {"cleaned": cleaned, "message": f"Cleaned up {cleaned} expired reservations"}
