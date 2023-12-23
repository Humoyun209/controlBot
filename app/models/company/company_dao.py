from db import async_session_maker
from models.company.models import Company

from sqlalchemy import insert, select


class CompanyDAO:
    @classmethod
    async def get_company(cls, name: str):
        async with async_session_maker() as session:
            query = select(Company).where(Company.name == name)
            company = await session.execute(query)
            return company.fetchone()
    
    @classmethod
    async def create_company(cls, name: str, technical_map: str):
        async with async_session_maker() as session:
            company = await cls.get_company(name)
            if not company:
                query = insert(Company).values(
                    name=name,
                    technical_map=technical_map
                )
                await session.execute(query)
                await session.commit()
            return bool(company)
    
    @classmethod
    async def list_company(cls) -> list[Company]:
        async with async_session_maker() as session:
            data = await session.execute(select(Company))
            return data.scalars().all()