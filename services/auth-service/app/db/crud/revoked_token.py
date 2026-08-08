from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.revoked_token import RevokedToken


async def get_revoked_token_by_jti(
    session: AsyncSession,
    jti: str
) -> RevokedToken | None: 
    query = select(RevokedToken).where(RevokedToken.jti == jti)

    token = await session.scalar(query)
    return token
