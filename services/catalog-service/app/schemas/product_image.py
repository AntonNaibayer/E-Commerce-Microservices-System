import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductImageCreate(BaseModel):
    product_id: uuid.UUID
    url: str = Field(max_length=256)
    alt_text: str | None = Field(min_length=5, max_length=256, default=None)
    sort_order: int = Field(ge=1)

class ProductImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    product_id: uuid.UUID 
    url: str
    alt_text: str | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

class ProductImageUpdate(BaseModel):
    url: str | None = Field(default=None)
    alt_text: str | None = Field(min_length=5, max_length=256, default=None)
    sort_order: int | None = Field(ge=1, default=None)