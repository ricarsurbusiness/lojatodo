from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.core.dependencies import CurrentUser, require_admin
from app.schemas.admin_schema import (
    DashboardResponse,
    AdminUserListResponse,
    AdminOrderListResponse,
    UpdateOrderStatusRequest,
    UpdateOrderStatusResponse
)
from app.services import admin_service


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    current_user: CurrentUser = Depends(require_admin)
):
    data = await admin_service.get_dashboard_data(token=current_user.token)
    
    if data.get("errors"):
        for error in data["errors"]:
            if error.get("service"):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Service unavailable: {error['service']}"
                )
    
    return DashboardResponse(
        total_users=data["total_users"],
        total_orders=data["total_orders"],
        total_revenue=data["total_revenue"],
        recent_orders=data["recent_orders"],
        top_products=data["top_products"]
    )


@router.get("/users", response_model=AdminUserListResponse)
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(require_admin)
):
    data = await admin_service.get_users(page=page, limit=limit, search=search, role=role, token=current_user.token)
    
    # Transform items to match AdminUserResponse schema
    items = []
    for item in data.get("items", []):
        item_dict = {
            "id": item.get("id"),
            "email": item.get("email"),
            "name": item.get("name"),
            "role": item.get("roles", [None])[0] if item.get("roles") else None,
            "roles": item.get("roles"),
            "created_at": item.get("created_at")
        }
        items.append(item_dict)
    
    return AdminUserListResponse(
        items=items,
        total=data.get("total", 0),
        page=data.get("page", 1),
        limit=data.get("limit", 20),
        pages=data.get("pages", 1)
    )


@router.get("/orders", response_model=AdminOrderListResponse)
async def get_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: CurrentUser = Depends(require_admin)
):
    data = await admin_service.get_orders(
        page=page,
        limit=limit,
        status=status,
        start_date=start_date,
        end_date=end_date,
        token=current_user.token
    )
    
    return AdminOrderListResponse(
        items=data.get("items", []),
        total=data.get("total", 0),
        page=data.get("page", 1),
        limit=data.get("limit", 20),
        pages=data.get("pages", 1)
    )


@router.put("/orders/{order_id}/status", response_model=UpdateOrderStatusResponse)
async def update_order_status(
    order_id: int,
    request: UpdateOrderStatusRequest,
    current_user: CurrentUser = Depends(require_admin)
):
    valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
    
    if request.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Valid values: {valid_statuses}"
        )
    
    try:
        result = await admin_service.update_order_status(
            admin_id=current_user.user_id,
            order_id=order_id,
            new_status=request.status,
            token=current_user.token
        )
        
        return UpdateOrderStatusResponse(
            id=result.get("id"),
            status=result.get("status"),
            updated_at=result.get("updated_at")
        )
    except Exception as e:
        if "404" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order status"
        )
