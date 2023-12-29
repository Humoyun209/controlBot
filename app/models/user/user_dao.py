from models.enums import UserStatus
from db import async_session_maker
from models.user.models import User, Worker
from models.company.models import Company, CompanyWorker

from sqlalchemy import insert, select, update, delete, or_, and_, not_
from sqlalchemy.orm import selectinload, joinedload


class UserDAO:
    @classmethod
    async def update_user(cls, user_id, **kwargs):
        async with async_session_maker() as session:
            await session.execute(
                update(User)
                .where(User.id == user_id)
                .values(**kwargs)
            )
            await session.commit()
    
    @classmethod
    async def get_user(cls, user_id: int) -> User:
        async with async_session_maker() as session:
            user = await session.execute(
                select(User).where(User.id == user_id).options(joinedload(User.worker))
            )
            return user.scalars().first()

    @classmethod
    async def create_user(cls, **kwargs):
        user = await cls.get_user(kwargs.get("id"))
        if user is None:
            async with async_session_maker() as session:
                result = await session.execute(insert(User).values(**kwargs))
                await session.commit()
                return result
        return user

    @classmethod
    async def get_users_without_anonyms(cls):
        async with async_session_maker() as session:
            users = await session.execute(
                select(User).where(
                    User.status.in_([UserStatus.USER, UserStatus.ANONYMOUS]),
                )
            )
            return users.scalars().all()

    @classmethod
    async def anonymous_user_list(cls):
        async with async_session_maker() as session:
            result = await session.execute(
                select(User).where(User.status == UserStatus.ANONYMOUS)
            )
            return result.scalars().all()

    @classmethod
    async def change_user_status(cls, user_id, status: UserStatus):
        async with async_session_maker() as session:
            await session.execute(
                update(User).where(User.id == user_id).values(status=status)
            )
            await session.commit()

    @classmethod
    async def appoint_as_admin(cls, user_id):
        async with async_session_maker() as session:
            query = (
                update(User)
                .where(User.id == user_id)
                .values(
                    status=UserStatus.ADMIN,
                )
            )
            await session.execute(query)
            await session.commit()

    @classmethod
    async def delete_user(cls, user_id):
        async with async_session_maker() as session:
            query = delete(User).where(User.id == user_id)
            await session.execute(query)
            await session.commit()

    @classmethod
    async def get_super_admin(cls) -> User:
        async with async_session_maker() as session:
            admin = await session.execute(
                select(User).where(User.status == UserStatus.SUPER)
            )
            return admin.scalars().first()

    @classmethod
    async def get_workers(cls):
        async with async_session_maker() as session:
            users = await session.execute(
                select(User)
                .options(joinedload(User.worker))
                .where(User.worker != None)
            )
            return users.scalars().all()
    
    @classmethod
    async def get_admins(cls):
        async with async_session_maker() as session:
            users = await session.execute(
                select(User)
                .where(User.status == UserStatus.ADMIN)
            )
            return users.scalars().all()
    
    @classmethod
    async def get_users(cls):
        async with async_session_maker() as session:
            users = await session.execute(
                select(User)
                .options(joinedload(User.worker))
                .where(User.status == UserStatus.USER, User.worker == None)
            )
            return users.scalars().all()