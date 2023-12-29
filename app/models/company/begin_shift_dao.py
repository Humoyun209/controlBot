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

    @classmethod
    async def get_last_begin_shift_for_company_and_worker(
        cls, company_id: int, worker_id: int
    ) -> BeginShift:
        async with async_session_maker() as session:
            begin_shift = await session.execute(
                select(BeginShift)
                .where(
                    BeginShift.company_id == company_id,
                    BeginShift.worker_id == worker_id,
                )
                .order_by(BeginShift.created.desc())
            )
            return begin_shift.scalars().first()
