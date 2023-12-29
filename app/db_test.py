import asyncio
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from models.user.models import Worker, User
from models.user.user_dao import UserDAO
from models.user.worker_dao import WorkerDAO
from models.company.models import BeginShift, EndShift, Company, CompanyWorker
from models.company.begin_shift_dao import BeginShiftDAO
from db import async_session_maker


async def query():
    async with async_session_maker() as session:
        # query = (
        #     select(User.id, Worker.id, Worker.user_id)
        #     .select_from(User)
        #     .join(Worker, Worker.user_id == User.id)
        #     .where(User.id == 6652099976)
        # )

        query = (
            select(User).where(User.id == 66520999763).options(joinedload(User.worker))
        )
        begin_shift = await session.execute(query)

        print(begin_shift.scalars().first().worker)


asyncio.run(query())
