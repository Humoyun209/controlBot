from db import async_session_maker
from models.user.models import User, UserStatus

from sqlalchemy import insert


class UserDAO:
    @classmethod
    async def get_user(cls, user_id: int):
        async with async_session_maker() as session:
            user = await session.get(User, user_id)
            return user
    
    @classmethod
    async def create_user(cls, user_id, username, status: UserStatus):
        user = await cls.get_user(user_id)
        if user is None:
            async with async_session_maker() as session:
                result = await session.execute(
                    insert(User).values(
                        id=user_id,
                        username=username,
                        status=status,
                    )
                )
                await session.commit()
                return result
        return user
        
    