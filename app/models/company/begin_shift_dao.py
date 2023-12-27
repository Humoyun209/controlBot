from models.company.models import BeginShift, EndShift, Company
from models.user.models import Worker
from db import async_session_maker
from sqlalchemy import select, insert, update, delete


class BeginShiftDAO:
    @classmethod
    async def create_begin_shift(cls, **kwargs):
        async with async_session_maker() as session:
            query = insert(BeginShift).values(**kwargs)
            await session.execute(query)
            await session.commit()