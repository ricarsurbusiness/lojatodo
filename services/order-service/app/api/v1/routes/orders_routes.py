from math import ceil
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import httpx

from app.core.dependencies import CurrentUser, get_current_user
from app.db.session import get_db
from app.models.order_model import OrderStatus
from app.schemas.order_schema import (
    CancelOrderResponse,
    OrderCreateRequest,
    OrderDetailResponse,
    OrderItemResponse,
    OrderListResponse,
    OrderSummaryResponse,
    ShippingAddress,
    ShipOrderRequest,
    ShipOrderResponse,
)
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])


def to_order_detail(order) -> OrderDetailResponse:
    return OrderDetailResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total_amount=order.total_amount,
        shipping_address=ShippingAddress(
            street=order.shipping_street,
            city=order.shipping_city,
            state=order.shipping_state,
            zip_code=order.shipping_zip_code,
            country=order.shipping_country,
        ),
        payment_id=order.payment_id,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=[
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in order.items
        ],
    )


@router.post("", response_model=OrderDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreateRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrderService(db)

    try:
        order = await service.create_order(
            current_user.user_id, 
            payload, 
            current_user.email,
            token=current_user.token  # Pass the JWT token to internal calls
        )
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 409:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient stock")
        if exc.response.status_code == 402:
            raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Payment failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Service coordination failed")

    return to_order_detail(order)


class ConfirmOrderResponse(BaseModel):
    id: int
    status: OrderStatus
    payment_id: int
    updated_at: datetime


@router.put("/{order_id}/confirm", response_model=ConfirmOrderResponse)
async def confirm_order(
    order_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Confirm a pending order (process payment)"""
    service = OrderService(db)

    try:
        order = await service.confirm_order(
            order_id=order_id,
            user_email=current_user.email,
            token=current_user.token,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 402:
            raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Payment failed")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Service coordination failed")

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return ConfirmOrderResponse(id=order.id, status=order.status, payment_id=order.payment_id, updated_at=order.updated_at)


@router.get("", response_model=OrderListResponse)
async def list_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrderService(db)
    items, total = await service.list_orders(current_user.user_id, page, limit)
    pages = ceil(total / limit) if total > 0 else 0

    return OrderListResponse(
        items=[
            OrderSummaryResponse(
                id=item.id,
                user_id=item.user_id,
                status=item.status,
                total_amount=item.total_amount,
                created_at=item.created_at,
            )
            for item in items
        ],
        total=total,
        page=page,
        pages=pages,
    )


@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order(
    order_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrderService(db)
    # Allow admins to view any order
    if "admin" in current_user.roles or "superAdmin" in current_user.roles:
        order = await service.get_order_admin(order_id)
    else:
        order = await service.get_order(current_user.user_id, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return to_order_detail(order)


@router.put("/{order_id}/cancel", response_model=CancelOrderResponse)
async def cancel_order(
    order_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = OrderService(db)

    try:
        order = await service.cancel_order(current_user.user_id, order_id, token=current_user.token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return CancelOrderResponse(id=order.id, status=order.status, updated_at=order.updated_at)


@router.put("/{order_id}/ship", response_model=ShipOrderResponse)
async def ship_order(
    order_id: int,
    request: ShipOrderRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if "admin" not in current_user.roles and "superAdmin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")

    service = OrderService(db)

    try:
        order = await service.ship_order(
            order_id=order_id,
            tracking_number=request.tracking_number,
            carrier=request.carrier,
            estimated_delivery=str(request.estimated_delivery),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return ShipOrderResponse(
        id=order.id,
        status=order.status,
        tracking_number=order.tracking_number,
        carrier=order.carrier,
        updated_at=order.updated_at,
    )


@router.get("/admin/all", response_model=OrderListResponse)
async def list_all_orders_admin(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if "admin" not in current_user.roles and "superAdmin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")

    service = OrderService(db)
    items, total = await service.list_all_orders(page=page, limit=limit)
    pages = ceil(total / limit) if total > 0 else 0

    return OrderListResponse(
        items=[
            OrderSummaryResponse(
                id=item.id,
                user_id=item.user_id,
                status=item.status,
                total_amount=item.total_amount,
                created_at=item.created_at,
            )
            for item in items
        ],
        total=total,
        page=page,
        pages=pages,
    )


@router.get("/admin/count")
async def get_order_count_admin(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if "admin" not in current_user.roles and "superAdmin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")

    service = OrderService(db)
    count = await service.count_all_orders()
    return {"count": count}


class DeliverOrderResponse(BaseModel):
    id: int
    status: OrderStatus
    updated_at: datetime


@router.put("/{order_id}/deliver", response_model=DeliverOrderResponse)
async def deliver_order(
    order_id: int,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if "admin" not in current_user.roles and "superAdmin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")

    service = OrderService(db)

    try:
        order = await service.deliver_order(order_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return DeliverOrderResponse(id=order.id, status=order.status, updated_at=order.updated_at)


class UpdateStatusRequest(BaseModel):
    status: str


class UpdateStatusResponse(BaseModel):
    id: int
    status: str
    updated_at: datetime


@router.put("/{order_id}/status", response_model=UpdateStatusResponse)
async def update_order_status(
    order_id: int,
    request: UpdateStatusRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Only admins can update status directly
    if "admin" not in current_user.roles and "superAdmin" not in current_user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    
    service = OrderService(db)
    order = await service.get_order_admin(order_id)
    
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Map status string to OrderStatus enum
    status_map = {
        'pendiente': OrderStatus.PENDING,
        'confirmado': OrderStatus.CONFIRMED,
        'enviado': OrderStatus.SHIPPED,
        'entregado': OrderStatus.DELIVERED,
        'cancelado': OrderStatus.CANCELLED,
        'fallido': OrderStatus.FAILED,
    }
    
    new_status = status_map.get(request.status.lower(), OrderStatus.PENDING)
    order.status = new_status
    
    updated_order = await service.repo.update_order(order)
    
    return UpdateStatusResponse(
        id=updated_order.id,
        status=request.status,
        updated_at=updated_order.updated_at
    )
