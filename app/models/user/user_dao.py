from models.enums import UserStatus
from db import async_session_maker
from models.user.models import User, Worker
from models.company.models import Company, CompanyWorker

from sqlalchemy import insert, select, update, delete, or_, and_, not_
from sqlalchemy.orm import selectinload, joinedload


class UserDAO:
    @classmethod
    async def get_user(cls, user_id: int) -> User:
        async with async_session_maker() as session:
            user = await session.execute(
                select(User)
                .where(User.id == user_id)
                .options(joinedload(User.worker))
            )
            return user.scalars().first()
        
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


class WorkerDAO:
    @classmethod
    async def get_worker_by_id(cls, worker_id):
        async with async_session_maker() as session:
            user = await session.execute(
                select(Worker).where(Worker.id == worker_id)
            )
            return user.scalars().first()
    
    @classmethod
    async def get_worker_with_companies_for_shift(cls, worker_id, live: bool) -> Worker:
        async with async_session_maker() as session:
            worker = await session.execute(
                select(Worker.id, Company.id, Company.name)
                .select_from(Worker)
                .join(CompanyWorker, CompanyWorker.worker_id == Worker.id)
                .join(Company, Company.id == CompanyWorker.company_id)
                .where(Worker.id == worker_id, Company.live == live, Company.is_active == True)
            )
            return worker.all()

    async def worker_list(cls):
        async with async_session_maker() as session:
            result = await session.execute(
                select(Worker).where(Worker.is_active == True)
            )
            return result.scalars().all()

    @classmethod
    async def get_worker_by_user_id(cls, user_id: int) -> Worker:
        async with async_session_maker() as session:
            worker = await session.execute(select(Worker).where(Worker.user_id == user_id))
            return worker.scalars().first()

    @classmethod
    async def worker_create(cls, user_id: int) -> Worker:
        async with async_session_maker() as session:
            worker = await cls.get_worker_by_user_id(user_id)
            if not worker:
                query = insert(Worker).values(user_id=user_id)
                await session.execute(query)
                await session.commit()
                worker = await cls.get_worker_by_user_id(user_id)
            return worker

    @classmethod
    async def toggle_company_to_worker(cls, worker_id, company_name: str):
        async with async_session_maker() as session:
            company = await session.execute(
                select(Company).where(Company.name == company_name)
            )
            company = company.scalars().first()
            result = await session.execute(
                select(Worker)
                .where(Worker.id == worker_id)
                .options(selectinload(Worker.companies))
            )
            worker: Worker = result.scalars().first()
            if company not in worker.companies:
                worker.companies.append(company)
            else:
                worker.companies.remove(company)
            await session.commit()
            