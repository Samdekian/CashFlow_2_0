"""
Category API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID

from ....database import get_db
from ....services.category_service import CategoryService
from ....schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryTreeResponse,
    CategoryListResponse,
    CategoryFilters,
    CategoryBulkOperation,
    CategoryStatistics
)
from ....schemas.common import SuccessResponse

router = APIRouter()


@router.get("/", response_model=CategoryListResponse)
async def get_categories(
    level: Optional[int] = Query(None, ge=1, le=3, description="Filter by category level"),
    parent_id: Optional[UUID] = Query(None, description="Filter by parent category ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_system: Optional[bool] = Query(None, description="Filter by system category status"),
    search: Optional[str] = Query(None, description="Search in name and description"),
    db: Session = Depends(get_db)
):
    """Get categories with optional filtering."""
    try:
        # Build filters
        filters = None
        if any([level, parent_id, is_active, is_system, search]):
            filters = CategoryFilters(
                level=level,
                parent_id=parent_id,
                is_active=is_active,
                is_system=is_system,
                search_query=search
            )
        
        category_service = CategoryService(db)
        result = category_service.get_categories(filters=filters)
        
        return CategoryListResponse(
            categories=result.items,
            total=result.total
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/tree", response_model=List[CategoryTreeResponse])
async def get_category_tree(
    db: Session = Depends(get_db)
):
    """Get the complete category hierarchy tree."""
    try:
        category_service = CategoryService(db)
        tree = category_service.get_category_tree()
        return tree
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific category by ID."""
    try:
        category_service = CategoryService(db)
        category = category_service.get_category(category_id)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return category
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new category."""
    try:
        category_service = CategoryService(db)
        category = category_service.create_category(category_data)
        return category
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    update_data: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing category."""
    try:
        category_service = CategoryService(db)
        category = category_service.update_category(category_id, update_data)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return category
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{category_id}", response_model=SuccessResponse)
async def delete_category(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a category."""
    try:
        category_service = CategoryService(db)
        success = category_service.delete_category(category_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return SuccessResponse(message="Category deleted successfully")
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/bulk", response_model=dict)
async def bulk_category_operation(
    operation_data: CategoryBulkOperation,
    db: Session = Depends(get_db)
):
    """Perform bulk operations on categories."""
    try:
        category_service = CategoryService(db)
        results = category_service.bulk_operation(operation_data)
        return results
        
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{category_id}/children", response_model=List[CategoryResponse])
async def get_category_children(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """Get child categories for a specific category."""
    try:
        category_service = CategoryService(db)
        children = category_service.get_category_children(category_id)
        return children
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{category_id}/ancestors", response_model=List[CategoryResponse])
async def get_category_ancestors(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """Get ancestor categories for a specific category."""
    try:
        category_service = CategoryService(db)
        ancestors = category_service.get_category_ancestors(category_id)
        return ancestors
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{category_id}/descendants", response_model=List[CategoryResponse])
async def get_category_descendants(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """Get descendant categories for a specific category."""
    try:
        category_service = CategoryService(db)
        descendants = category_service.get_category_descendants(category_id)
        return descendants
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{category_id}/statistics", response_model=CategoryStatistics)
async def get_category_statistics(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """Get statistics for a specific category."""
    try:
        category_service = CategoryService(db)
        statistics = category_service.get_category_statistics(category_id)
        return statistics
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/level/{level}", response_model=List[CategoryResponse])
async def get_categories_by_level(
    level: int,
    db: Session = Depends(get_db)
):
    """Get all categories at a specific level."""
    try:
        if level < 1 or level > 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Level must be between 1 and 3"
            )
        
        category_service = CategoryService(db)
        categories = category_service.get_categories_by_level(level)
        return categories
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/primary/list", response_model=List[CategoryResponse])
async def get_primary_categories(
    db: Session = Depends(get_db)
):
    """Get all primary (level 1) categories."""
    try:
        category_service = CategoryService(db)
        categories = category_service.get_primary_categories()
        return categories
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/secondary/list", response_model=List[CategoryResponse])
async def get_secondary_categories(
    db: Session = Depends(get_db)
):
    """Get all secondary (level 2) categories."""
    try:
        category_service = CategoryService(db)
        categories = category_service.get_secondary_categories()
        return categories
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/detailed/list", response_model=List[CategoryResponse])
async def get_detailed_categories(
    db: Session = Depends(get_db)
):
    """Get all detailed (level 3) categories."""
    try:
        category_service = CategoryService(db)
        categories = category_service.get_detailed_categories()
        return categories
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{category_id}/activate", response_model=CategoryResponse)
async def activate_category(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """Activate a category."""
    try:
        category_service = CategoryService(db)
        category = category_service.activate_category(category_id)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return category
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{category_id}/deactivate", response_model=CategoryResponse)
async def deactivate_category(
    category_id: UUID,
    db: Session = Depends(get_db)
):
    """Deactivate a category."""
    try:
        category_service = CategoryService(db)
        category = category_service.deactivate_category(category_id)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return category
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/open-finance/standards", response_model=dict)
async def get_open_finance_standards(
    db: Session = Depends(get_db)
):
    """Get Open Finance Brasil standards information."""
    try:
        from ....core.open_finance_standards import get_open_finance_compliance_info
        
        compliance_info = get_open_finance_compliance_info()
        
        # Get category counts from database
        category_service = CategoryService(db)
        category_counts = category_service.get_category_counts_by_level()
        
        return {
            "compliance_info": compliance_info,
            "category_counts": category_counts
        }
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
