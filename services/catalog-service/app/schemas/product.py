import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.enums.currency import Currency


class ProductCreate(BaseModel):
    name: str = Field(min_length=5, max_length=256)
    sku: str = Field(min_length=1, max_length=256)
    description: str = Field(min_length=30, max_length=512)
    base_price: Decimal = Field(gt=0, )
    currency: Currency = Field(default=Currency.RUB)
    category_id: uuid.UUID
    brand_id: uuid.UUID | None = Field(default=None)
    attributes: dict = Field(default_factory=dict)
    is_active: bool = Field(default=True)

class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    sku: str
    description: str
    base_price: Decimal
    currency: Currency
    category_id: uuid.UUID
    brand_id: uuid.UUID | None
    attributes: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @field_serializer('base_price')
    def serialize_price(self, price: Decimal, _info):
        return str(price) 

class ProductUpdate(BaseModel):
    name: str | None = Field(min_length=5, max_length=256, default=None)
    sku: str | None = Field(min_length=1, max_length=256, default=None)
    description: str | None = Field(min_length=30, max_length=512, default=None)
    base_price: Decimal | None = Field(gt=0, default=None)
    currency: Currency | None = Field(default=None)
    category_id: uuid.UUID | None = Field(default=None)
    brand_id: uuid.UUID | None = Field(default=None)
    attributes: dict | None = Field(default=None)
    is_active: bool | None = Field(default=None)