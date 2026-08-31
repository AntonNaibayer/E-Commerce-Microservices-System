import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class ProductVariantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID
    sku: str
    attributes: dict
    price_override: Decimal | None
    stock_quantity: int
    created_at: datetime
    updated_at: datetime

    @field_serializer('price_override')
    def serialize_price(self, price: Decimal, _info):
        return str(price) 

class ProductVariantCreate(BaseModel):
    product_id: uuid.UUID
    sku: str = Field(min_length=1, max_length=256)
    attributes: dict = Field(default_factory=dict)
    price_override: Decimal | None = Field(gt=0, default=None)
    stock_quantity: int = Field(ge=0, default=0)
    

class ProductVariantUpdate(BaseModel):
    product_id: uuid.UUID | None = Field(default=None)
    sku: str | None = Field(min_length=1, max_length=256, default=None)
    attributes: dict | None = Field(default=None)
    price_override: Decimal | None = Field(gt=0, default=None)
    stock_quantity: int | None = Field(ge=0, default=None)