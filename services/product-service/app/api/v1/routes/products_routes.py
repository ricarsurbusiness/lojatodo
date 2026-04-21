from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import httpx

from app.db.session import get_db
from app.schemas.product_schema import ProductCreate, ProductResponse, ProductUpdate, ProductListResponse
from app.services.product_service import ProductService
from app.core.dependencies import get_current_user, CurrentUser, require_role

router = APIRouter(prefix="/products", tags=["products"])

# Inventory service URL - internal Docker network
INVENTORY_SERVICE_URL = "http://inventory-service:8005/api/v1/inventory"


@router.get("", response_model=List[ProductListResponse])
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    product_service = ProductService(db)
    products = await product_service.list_products(skip=skip, limit=limit, search=search)
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    product_service = ProductService(db)
    product = await product_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    request: ProductCreate,
    current_user: CurrentUser = Depends(require_role(["admin", "superAdmin"])),
    db: AsyncSession = Depends(get_db)
):
    product_service = ProductService(db)
    product = await product_service.create_product(
        name=request.name,
        description=request.description,
        price=request.price,
        category_id=request.category_id
    )
    
    # Create inventory for the product with initial stock
    if request.stock > 0:
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    INVENTORY_SERVICE_URL,
                    json={"product_id": product.id, "quantity": request.stock}
                )
            except Exception as e:
                # Log error but don't fail product creation
                print(f"Failed to create inventory: {e}")
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    request: ProductUpdate,
    current_user: CurrentUser = Depends(require_role(["admin", "superAdmin"])),
    db: AsyncSession = Depends(get_db)
):
    product_service = ProductService(db)
    product = await product_service.update_product(
        product_id=product_id,
        name=request.name,
        description=request.description,
        price=request.price,
        category_id=request.category_id
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update inventory stock if provided
    if request.stock is not None:
        async with httpx.AsyncClient() as client:
            try:
                # First try to get existing inventory
                response = await client.get(f"{INVENTORY_SERVICE_URL}/{product_id}")
                if response.status_code == 200:
                    # Update existing inventory - need to adjust quantity
                    inventory = response.json()
                    current_qty = inventory.get("quantity", 0)
                    # Update: PUT to replace or POST to add
                    await client.put(
                        f"{INVENTORY_SERVICE_URL}/{product_id}",
                        json={"quantity": request.stock}
                    )
                else:
                    # Create new inventory
                    await client.post(
                        INVENTORY_SERVICE_URL,
                        json={"product_id": product_id, "quantity": request.stock}
                    )
            except Exception as e:
                print(f"Failed to update inventory: {e}")
    
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: CurrentUser = Depends(require_role(["admin", "superAdmin"])),
    db: AsyncSession = Depends(get_db)
):
    product_service = ProductService(db)
    deleted = await product_service.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return None
