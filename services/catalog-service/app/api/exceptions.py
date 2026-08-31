from fastapi import HTTPException, status

# ---------------------------------------------------------------------------
# Brand
# ---------------------------------------------------------------------------

brand_creation_conflict_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Cannot create brand",
)

brand_update_conflict_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Cannot update brand",
)

duplicate_brand_slug_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Brand with that slug already exists",
)

not_found_brand_error = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Brand not found",
)

brand_deletion_conflict_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Cannot delete brand",
)

# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

category_creation_conflict_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Cannot create category",
)

category_update_conflict_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Cannot update category",
)

duplicate_category_slug_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Category with that slug already exists",
)

not_found_category_error = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Category not found",
)

not_found_parent_category_error = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Parent category not found",
)

category_deletion_conflict_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Cannot delete category",
)

# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------

duplicate_product_sku_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Product with that sku already exists",
)

duplicate_product_slug_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Product with that slug already exists",
)

product_creation_conflict_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Cannot create product",
)

product_update_conflict_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Cannot update product",
)

not_found_product_error = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Product not found",
)

product_deletion_conflict_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Cannot delete product",
)

# ---------------------------------------------------------------------------
# Product image
# ---------------------------------------------------------------------------

product_image_creation_conflict_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Cannot create product image",
)

product_image_update_conflict_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Cannot update product image",
)

not_found_product_image_error = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Product image not found",
)

product_image_deletion_conflict_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Cannot delete product image",
)

# ---------------------------------------------------------------------------
# Product variant
# ---------------------------------------------------------------------------

duplicate_product_variant_sku_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Product variant with that sku already exists",
)

product_variant_creation_conflict_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Cannot create product variant",
)

product_variant_update_conflict_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Cannot update product variant",
)

not_found_product_variant_error = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Product variant not found",
)

product_variant_deletion_conflict_error = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Cannot delete product variant",
)