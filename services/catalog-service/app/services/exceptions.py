import uuid
from decimal import Decimal

# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class DuplicateCategorySlugError(Exception):
    """Возникает, если такой slug уже существует"""

    def __init__(self, slug: str) -> None:
        self.slug = slug
        super().__init__(f"Category with slug '{slug}' already exists")


class CategoryCreationConflictError(Exception):
    """Возникает, если не удалось создать категорию в бд"""

    def __init__(self, name: str, slug: str) -> None:
        self.name = name
        self.slug = slug
        super().__init__(f"Cannot create category: name={name!r}, slug={slug!r}")


class CategoryUpdateConflictError(Exception):
    """Возникает, если не удалось обновить категорию из-за конфликта данных (дубликат slug)"""

    def __init__(self, category_id: uuid.UUID, **conflicting_fields) -> None:
        self.category_id = category_id
        self.conflicting_fields = conflicting_fields
        fields_str = ", ".join(f"{k}={v!r}" for k, v in conflicting_fields.items())
        super().__init__(f"Cannot update category '{category_id}': conflict on {fields_str}")


class NotFoundCategoryError(Exception):
    """Возникает, если такой категории не существует"""

    def __init__(self, identifier: uuid.UUID | str) -> None:
        self.identifier = identifier
        super().__init__(f"Category '{identifier}' not found")


class NotFoundParentCategoryError(Exception):
    """Возникает, если такой родительской категории не существует"""

    def __init__(self, identifier: uuid.UUID | str) -> None:
        self.identifier = identifier
        super().__init__(f"Parent category '{identifier}' not found")


class CategoryDeletionConflictError(Exception):
    """Возникает, если категорию нельзя удалить из-за связанных данных"""

    def __init__(self, category_id: uuid.UUID) -> None:
        self.category_id = category_id
        super().__init__(f"Cannot delete category '{category_id}': related data exists")


# ---------------------------------------------------------------------------
# Brand
# ---------------------------------------------------------------------------

class BrandCreationConflictError(Exception):
    """Возникает, если не удалось создать бренд в бд"""

    def __init__(self, name: str, slug: str) -> None:
        self.name = name
        self.slug = slug
        super().__init__(f"Cannot create brand: name={name!r}, slug={slug!r}")


class BrandUpdateConflictError(Exception):
    """Возникает, если не удалось обновить бренд из-за конфликта данных (дубликат slug)"""

    def __init__(self, brand_id: uuid.UUID, **conflicting_fields) -> None:
        self.brand_id = brand_id
        self.conflicting_fields = conflicting_fields
        fields_str = ", ".join(f"{k}={v!r}" for k, v in conflicting_fields.items())
        super().__init__(f"Cannot update brand '{brand_id}': conflict on {fields_str}")


class DuplicateBrandSlugError(Exception):
    """Возникает, если такой slug уже существует"""

    def __init__(self, slug: str) -> None:
        self.slug = slug
        super().__init__(f"Brand with slug '{slug}' already exists")


class NotFoundBrandError(Exception):
    """Возникает, если такой brand не существует"""

    def __init__(self, identifier: uuid.UUID | str) -> None:
        self.identifier = identifier
        super().__init__(f"Brand '{identifier}' not found")


class BrandDeletionConflictError(Exception):
    """Возникает, если бренд нельзя удалить из-за связанных данных"""

    def __init__(self, brand_id: uuid.UUID) -> None:
        self.brand_id = brand_id
        super().__init__(f"Cannot delete brand '{brand_id}': related data exists")


# ---------------------------------------------------------------------------
# Product
# ---------------------------------------------------------------------------

class DuplicateProductSlugError(Exception):
    """Возникает, если такой slug уже существует"""

    def __init__(self, slug: str) -> None:
        self.slug = slug
        super().__init__(f"Product with slug '{slug}' already exists")


class DuplicateProductSkuError(Exception):
    """Возникает, если такой sku уже существует"""

    def __init__(self, sku: str) -> None:
        self.sku = sku
        super().__init__(f"Product with sku '{sku}' already exists")


class ProductCreationConflictError(Exception):
    """Возникает, если не удалось создать продукт в бд"""

    def __init__(self, product_name: str, sku: str, slug: str) -> None:
        self.product_name = product_name
        self.sku = sku
        self.slug = slug
        super().__init__(
            f"Cannot create product: product_name={product_name!r}, "
            f"sku={sku!r}, slug={slug!r}"
        )


class ProductUpdateConflictError(Exception):
    """Возникает, если не удалось обновить продукт из-за конфликта данных (дубликат sku/slug)"""

    def __init__(self, product_id: uuid.UUID, **conflicting_fields) -> None:
        self.product_id = product_id
        self.conflicting_fields = conflicting_fields
        fields_str = ", ".join(f"{k}={v!r}" for k, v in conflicting_fields.items())
        super().__init__(f"Cannot update product '{product_id}': conflict on {fields_str}")


class NotFoundProductError(Exception):
    """Возникает, если такого продукта не существует"""

    def __init__(self, identifier: uuid.UUID | str) -> None:
        self.identifier = identifier
        super().__init__(f"Product '{identifier}' not found")


class ProductDeletionConflictError(Exception):
    """Возникает, если продукт нельзя удалить из-за связанных данных"""

    def __init__(self, product_id: uuid.UUID) -> None:
        self.product_id = product_id
        super().__init__(f"Cannot delete product '{product_id}': related data exists")


# ---------------------------------------------------------------------------
# Product image
# ---------------------------------------------------------------------------

class ProductImageCreationConflictError(Exception):
    """Возникает, если не удалось создать изображение продукта в бд"""

    def __init__(
        self,
        product_id: uuid.UUID,
        url: str,
        sort_order: int,
        alt_text: str | None = None,
    ) -> None:
        self.product_id = product_id
        self.url = url
        self.sort_order = sort_order
        self.alt_text = alt_text
        super().__init__(
            f"Cannot create product image: product_id={product_id!r}, "
            f"url={url!r}, sort_order={sort_order!r}, alt_text={alt_text!r}"
        )


class ProductImageUpdateConflictError(Exception):
    """Возникает, если не удалось обновить изображение продукта из-за конфликта данных"""

    def __init__(self, product_image_id: uuid.UUID, **conflicting_fields) -> None:
        self.product_image_id = product_image_id
        self.conflicting_fields = conflicting_fields
        fields_str = ", ".join(f"{k}={v!r}" for k, v in conflicting_fields.items())
        super().__init__(f"Cannot update product image '{product_image_id}': conflict on {fields_str}")


class ProductImageDeletionConflictError(Exception):
    """Возникает, если не удалось удалить изображение продукта в бд"""

    def __init__(self, product_image_id: uuid.UUID) -> None:
        self.product_image_id = product_image_id
        super().__init__(f"Cannot delete product image '{product_image_id}': related data exists")


class NotFoundProductImageError(Exception):
    """Возникает, если не существует изображение продукта с таким product_image_id"""

    def __init__(self, product_image_id: uuid.UUID) -> None:
        self.product_image_id = product_image_id
        super().__init__(f"Product image '{product_image_id}' not found")


# ---------------------------------------------------------------------------
# Product variant
# ---------------------------------------------------------------------------

class DuplicateProductVariantSkuError(Exception):
    """Возникает, если такой sku уже существует"""

    def __init__(self, sku: str) -> None:
        self.sku = sku
        super().__init__(f"Product variant with sku '{sku}' already exists")


class ProductVariantCreationConflictError(Exception):
    """Возникает, если не удалось создать вариант продукта в бд"""

    def __init__(
        self,
        product_id: uuid.UUID,
        sku: str,
        attributes: dict,
        stock_quantity: int,
        price_override: Decimal | None = None,
    ) -> None:
        self.product_id = product_id
        self.sku = sku
        self.attributes = attributes
        self.stock_quantity = stock_quantity
        self.price_override = price_override
        super().__init__(
            f"Cannot create product variant: product_id={product_id!r}, sku={sku!r}, "
            f"attributes={attributes!r}, stock_quantity={stock_quantity!r}, "
            f"price_override={price_override!r}"
        )


class ProductVariantUpdateConflictError(Exception):
    """Возникает, если не удалось обновить вариант продукта из-за конфликта данных (дубликат sku)"""

    def __init__(self, product_variant_id: uuid.UUID, **conflicting_fields) -> None:
        self.product_variant_id = product_variant_id
        self.conflicting_fields = conflicting_fields
        fields_str = ", ".join(f"{k}={v!r}" for k, v in conflicting_fields.items())
        super().__init__(f"Cannot update product variant '{product_variant_id}': conflict on {fields_str}")


class ProductVariantDeletionConflictError(Exception):
    """Возникает, если не удалось удалить вариант продукта в бд"""

    def __init__(self, product_variant_id: uuid.UUID) -> None:
        self.product_variant_id = product_variant_id
        super().__init__(f"Cannot delete product variant '{product_variant_id}': related data exists")


class NotFoundProductVariantError(Exception):
    """Возникает, если не существует варианта продукта с таким идентификатором"""

    def __init__(self, identifier: uuid.UUID | str) -> None:
        self.identifier = identifier
        super().__init__(f"Product variant '{identifier}' not found")