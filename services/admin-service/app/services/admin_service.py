from typing import Dict, Any, List, Optional
from decimal import Decimal

from app.services.clients import (
    get_auth_client,
    get_order_client,
    get_payment_client,
    get_analytics_client,
    AuthServiceClient,
    OrderServiceClient,
)
from app.services.audit_service import audit_log


async def get_dashboard_data(token: Optional[str] = None) -> Dict[str, Any]:
    errors = []
    auth = get_auth_client(token)
    order = get_order_client(token)
    payment = get_payment_client(token)
    analytics = get_analytics_client(token)
    
    try:
        total_users = await auth.get_user_count()
    except Exception as e:
        total_users = 0
        errors.append({"service": "auth", "error": str(e)})
    
    try:
        total_orders = await order.get_order_count()
    except Exception as e:
        total_orders = 0
        errors.append({"service": "order", "error": str(e)})
    
    try:
        revenue_data = await payment.get_total_revenue()
        total_revenue = Decimal(str(revenue_data.get("total_revenue", 0)))
    except Exception as e:
        total_revenue = Decimal("0")
        errors.append({"service": "payment", "error": str(e)})
    
    try:
        orders_data = await order.get_orders(page=1, limit=10)
        recent_orders = [
            {
                "id": o.get("id"),
                "user_id": o.get("user_id"),
                "status": o.get("status"),
                "total_amount": Decimal(str(o.get("total_amount", 0))),
                "created_at": o.get("created_at")
            }
            for o in orders_data.get("items", [])
        ]
    except Exception as e:
        recent_orders = []
        errors.append({"service": "order", "error": str(e)})
    
    try:
        top_products_data = await analytics.get_top_products(limit=10)
        top_products = [
            {
                "product_id": p.get("product_id"),
                "name": p.get("name", ""),
                "quantity_sold": p.get("quantity_sold", 0),
                "revenue": Decimal(str(p.get("revenue", 0)))
            }
            for p in top_products_data
        ]
    except Exception as e:
        top_products = []
        errors.append({"service": "analytics", "error": str(e)})
    
    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "recent_orders": recent_orders,
        "top_products": top_products,
        "errors": errors
    }


async def get_users(page: int = 1, limit: int = 20, search: Optional[str] = None, role: Optional[str] = None, token: Optional[str] = None) -> Dict[str, Any]:
    auth = get_auth_client(token)
    return await auth.get_users(page=page, limit=limit, search=search, role=role)


async def get_orders(page: int = 1, limit: int = 20, status: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None, token: Optional[str] = None) -> Dict[str, Any]:
    order = get_order_client(token)
    return await order.get_orders(page=page, limit=limit, status=status, start_date=start_date, end_date=end_date)


async def update_order_status(admin_id: int, order_id: int, new_status: str, token: Optional[str] = None) -> Dict[str, Any]:
    order = get_order_client(token)
    result = await order.update_order_status(order_id, new_status)
    
    await audit_log(
        admin_id=admin_id,
        action="update_order_status",
        details={
            "order_id": order_id,
            "new_status": new_status
        }
    )
    
    return result
