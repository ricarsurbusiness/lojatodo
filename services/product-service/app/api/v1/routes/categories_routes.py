from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.session import get_db
from app.schemas.category_schema import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services.category_service import CategoryService
from app.core.dependencies import get_current_user, CurrentUser, require_role

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db)
):
    category_service = CategoryService(db)
    categories = await category_service.list_categories()
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    category_service = CategoryService(db)
    category = await category_service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    request: CategoryCreate,
    current_user: CurrentUser = Depends(require_role(["admin", "superAdmin"])),
    db: AsyncSession = Depends(get_db)
):
    category_service = CategoryService(db)
    try:
        category = await category_service.create_category(
            name=request.name,
            description=request.description,
            parent_id=request.parent_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    request: CategoryUpdate,
    current_user: CurrentUser = Depends(require_role(["admin", "superAdmin"])),
    db: AsyncSession = Depends(get_db)
):
    category_service = CategoryService(db)
    try:
        category = await category_service.update_category(
            category_id=category_id,
            name=request.name,
            description=request.description
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: CurrentUser = Depends(require_role(["admin", "superAdmin"])),
    db: AsyncSession = Depends(get_db)
):
    category_service = CategoryService(db)
    deleted = await category_service.delete_category(category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    return None
