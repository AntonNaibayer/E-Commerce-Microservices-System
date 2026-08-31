from fastapi import APIRouter

from app.api.v1.brand import router as brand_router
from app.api.v1.category import router as category_router
from app.api.v1.product import router as product_router
from app.api.v1.product_image import router as product_image_router
from app.api.v1.product_variant import router as product_variant_router

router = APIRouter()
router.include_router(category_router)
router.include_router(brand_router)
router.include_router(product_router)
router.include_router(product_image_router)
router.include_router(product_variant_router)