from typing import Optional, Dict, Any, List
import httpx

from app.core.config import admin_settings


class ServiceClient:
    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url
        self.token = token
    
    def _get_headers(self) -> Dict[str, str]:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}{path}", params=params, headers=self._get_headers(), timeout=10.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise Exception(f"Service error: {e.response.status_code}")
            except httpx.RequestError:
                raise Exception(f"Service unavailable: {self.base_url}")
    
    async def put(self, path: str, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(f"{self.base_url}{path}", json=json_data, headers=self._get_headers(), timeout=10.0)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise Exception(f"Service error: {e.response.status_code}")
            except httpx.RequestError:
                raise Exception(f"Service unavailable: {self.base_url}")


class AuthServiceClient(ServiceClient):
    def __init__(self, token: Optional[str] = None):
        super().__init__(admin_settings.AUTH_SERVICE_URL, token)
    
    async def get_users(self, page: int = 1, limit: int = 20, search: Optional[str] = None, role: Optional[str] = None) -> Dict[str, Any]:
        params = {"page": page, "limit": limit}
        if search:
            params["search"] = search
        if role:
            params["role"] = role
        return await self.get("/api/v1/users", params)
    
    async def get_user_count(self) -> int:
        try:
            data = await self.get("/api/v1/users/count")
            return data.get("count", 0)
        except:
            return 0


class OrderServiceClient(ServiceClient):
    def __init__(self, token: Optional[str] = None):
        super().__init__(admin_settings.ORDER_SERVICE_URL, token)
    
    async def get_orders(self, page: int = 1, limit: int = 20, status: Optional[str] = None, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        params = {"page": page, "limit": limit}
        if status:
            params["status"] = status
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return await self.get("/api/v1/orders/admin/all", params)
    
    async def get_order_count(self) -> int:
        try:
            data = await self.get("/api/v1/orders/admin/count")
            return data.get("count", 0)
        except:
            return 0
    
    async def update_order_status(self, order_id: int, status: str) -> Dict[str, Any]:
        return await self.put(f"/api/v1/orders/{order_id}/status", {"status": status})


class PaymentServiceClient(ServiceClient):
    def __init__(self, token: Optional[str] = None):
        super().__init__(admin_settings.PAYMENT_SERVICE_URL, token)
    
    async def get_total_revenue(self) -> Dict[str, Any]:
        try:
            return await self.get("/api/v1/payments/revenue")
        except:
            return {"total_revenue": 0}


class AnalyticsServiceClient(ServiceClient):
    def __init__(self, token: Optional[str] = None):
        super().__init__(admin_settings.ORDER_SERVICE_URL, token)
    
    async def get_top_products(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top selling products from order service"""
        try:
            data = await self.get("/api/v1/admin/products/top", {"limit": limit})
            return data.get("items", [])
        except:
            return []
    
    async def get_sales_metrics(self) -> Dict[str, Any]:
        """Get sales metrics from payment service"""
        try:
            return await self.get("/api/v1/admin/payments/summary")
        except:
            return {"total_revenue": "0", "today_revenue": "0", "week_revenue": "0", "month_revenue": "0"}
    
    async def get_orders_by_status(self) -> Dict[str, Any]:
        """Get orders grouped by status"""
        try:
            data = await self.get("/api/v1/admin/orders", {"limit": 100})
            items = data.get("items", [])
            
            by_status = {}
            for order in items:
                status = order.get("status", "pendiente")
                by_status[status] = by_status.get(status, 0) + 1
            
            return {"total_orders": data.get("total", 0), "by_status": by_status}
        except:
            return {"total_orders": 0, "by_status": {}}


def get_auth_client(token: Optional[str] = None) -> AuthServiceClient:
    return AuthServiceClient(token)

def get_order_client(token: Optional[str] = None) -> OrderServiceClient:
    return OrderServiceClient(token)

def get_payment_client(token: Optional[str] = None) -> PaymentServiceClient:
    return PaymentServiceClient(token)

def get_analytics_client(token: Optional[str] = None) -> AnalyticsServiceClient:
    return AnalyticsServiceClient(token)
