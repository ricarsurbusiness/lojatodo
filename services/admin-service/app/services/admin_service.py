from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime, timedelta

from app.services.clients import (
    get_auth_client,
    get_order_client,
    get_payment_client,
    AuthServiceClient,
    OrderServiceClient,
)
from app.services.audit_service import audit_log


async def get_dashboard_data(token: Optional[str] = None) -> Dict[str, Any]:
    errors = []
    auth = get_auth_client(token)
    order = get_order_client(token)
    payment = get_payment_client(token)
    
    try:
        total_users = await auth.get_user_count()
    except Exception as e:
        total_users = 0
        errors.append({"service": "auth", "error": str(e)})
    
    try:
        # Get all orders to calculate totals
        orders_data = await order.get_orders(page=1, limit=100)
        all_orders = orders_data.get("items", [])
        total_orders = orders_data.get("total", 0)
    except Exception as e:
        total_orders = 0
        all_orders = []
        errors.append({"service": "order", "error": str(e)})
    
    try:
        # Calculate revenue from orders directly
        total_revenue = Decimal("0")
        today = datetime.now().date()
        
        for o in all_orders:
            amount = Decimal(str(o.get("total_amount", 0)))
            total_revenue += amount
        
        # Calculate by period
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        week_revenue = Decimal("0")
        month_revenue = Decimal("0")
        
        for o in all_orders:
            created_at = o.get("created_at", "")
            if created_at:
                try:
                    order_date = datetime.fromisoformat(created_at.replace("Z", "")).date()
                    amount = Decimal(str(o.get("total_amount", 0)))
                    
                    if order_date >= month_ago:
                        month_revenue += amount
                    if order_date >= week_ago:
                        week_revenue += amount
                except:
                    pass
    except Exception as e:
        total_revenue = Decimal("0")
        week_revenue = Decimal("0")
        month_revenue = Decimal("0")
        errors.append({"service": "order", "error": str(e)})
    
    try:
        recent_orders = [
            {
                "id": o.get("id"),
                "user_id": o.get("user_id"),
                "status": o.get("status"),
                "total_amount": Decimal(str(o.get("total_amount", 0))),
                "created_at": o.get("created_at")
            }
            for o in orders_data.get("items", [])[:10]
        ]
    except Exception as e:
        recent_orders = []
        errors.append({"service": "order", "error": str(e)})
    
    # Get top products from order items (simplified)
    try:
        product_sales: Dict[str, Dict] = {}
        for o in all_orders:
            for item in o.get("items", []):
                product_id = str(item.get("product_id", "?"))
                if product_id not in product_sales:
                    product_sales[product_id] = {"quantity": 0, "revenue": Decimal("0"), "name": f"Product {product_id}"}
                qty = item.get("quantity", 1)
                price = Decimal(str(item.get("unit_price", 0)))
                product_sales[product_id]["quantity"] += qty
                product_sales[product_id]["revenue"] += price * qty
        
        top_products = sorted(
            [
                {
                    "product_id": pid,
                    "name": data["name"],
                    "quantity_sold": data["quantity"],
                    "revenue": data["revenue"]
                }
                for pid, data in product_sales.items()
            ],
            key=lambda x: x["quantity_sold"],
            reverse=True
        )[:10]
    except Exception as e:
        top_products = []
        errors.append({"service": "order", "error": str(e)})
    
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
