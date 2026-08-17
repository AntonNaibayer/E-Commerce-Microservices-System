import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User


async def get_user_by_id(
    session: AsyncSession,
    user_id: uuid.UUID
) -> User | None:
    query = (
        select(User)
        .where(User.id == user_id)
    )
    return await session.scalar(query)

async def get_user_by_email(
    session: AsyncSession,
    email: str
) -> User | None:
    query = (
        select(User)
        .where(User.email == email)
    )
    return await session.scalar(query)