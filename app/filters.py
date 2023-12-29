from aiogram.types import Message
from aiogram.filters import BaseFilter
from models.user.models import User, UserStatus
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db import async_session_maker


class IsWorker(BaseFilter):
    async def __call__(self, message: Message):
        async with async_session_maker() as session:
            user_id = message.from_user.id
            cursor = await session.execute(
                select(User)
                .where(User.id == user_id)
                .options(joinedload(User.worker))
            )
            user = cursor.scalars().first()
            return user and user.status == UserStatus.USER and user.worker


class IsUser(BaseFilter):
    async def __call__(self, message: Message):
        async with async_session_maker() as session:
            user_id = message.from_user.id
            cursor = await session.execute(
                select(User)
                .where(User.id == user_id)
                .options(joinedload(User.worker))
            )
            user = cursor.scalars().first()
            return user and user.status == UserStatus.USER and user.worker


class IsAdmin(BaseFilter):
    async def __call__(self, message: Message):
        async with async_session_maker() as session:
            user_id = message.from_user.id
            user: User = await session.get(User, user_id)
            if user:
                return user.status == UserStatus.ADMIN
            return False
        

class IsSuperAdmin(BaseFilter):
    async def __call__(self, message: Message):
        async with async_session_maker() as session:
            user_id = message.from_user.id
            user = await session.get(User, user_id)
            if user:
                return user.status == UserStatus.SUPER
            return False
