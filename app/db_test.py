import asyncio
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from models.user.models import *
from models.user.user_dao import UserDAO, WorkerDAO
from models.company.models import *
from db import async_session_maker


async def query():
    user = await WorkerDAO.get_worker_with_companies_for_begin_shift(6)
    print(user)


asyncio.run(query())
