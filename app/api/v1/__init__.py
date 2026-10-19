from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.brands import router as brand_router
from app.api.v1.customers import router as customer_router
from app.api.v1.categories import router as category_router
from app.api.v1.products import router as product_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(brand_router)
router.include_router(customer_router)
router.include_router(category_router)
router.include_router(product_router)

__all__ = ["router"]
