import asyncio
import pandas as pd
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
        users = await session.execute(
                select(
                    EndShift.id, EndShift.grams_of_tobacco,
                    EndShift.summa, EndShift.quantity_of_sold,
                    EndShift.promo_quantity, EndShift.card,
                    EndShift.cash, EndShift.in_club,
                    EndShift.in_club_card, EndShift.in_club_cash,
                    EndShift.tips
                )
                .select_from(EndShift)
                .where(EndShift.company_id == 2)
            )
        print(users.scalars().all()[1].worker)

