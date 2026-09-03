import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str = Field(
        min_length=5, 
        max_length=256
    )
    parent_id: uuid.UUID | None = None

class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str 
    slug: str 
    parent_id: uuid.UUID | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

class CategoryUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=5, 
        max_length=256,
    ) # type: ignore
    parent_id: uuid.UUID | None = None
    is_active: bool | None = None