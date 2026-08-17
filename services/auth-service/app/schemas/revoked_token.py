import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RevokedTokenCreate(BaseModel):
    jti: str
    expires_at: datetime

class RevokedTokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    jti: str
    expires_at: datetime
