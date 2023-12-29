from db import async_session_maker
from sqlalchemy import select, insert, update
from models.company.models import EndShift


class EndShiftDAO:
    @classmethod
    async def create_end_shift(cls, **kwargs) -> EndShift:
        async with async_session_maker() as session:
            shift = await session.execute(
                insert(EndShift).values(**kwargs).returning(EndShift)
            )
            await session.commit()
            return shift.scalars().first()