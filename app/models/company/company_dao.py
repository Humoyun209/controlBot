from db import async_session_maker
from models.company.models import Company

from sqlalchemy import insert, select, update, delete


class CompanyDAO:
    @classmethod
    async def get_company(cls, name: str) -> Company:
        async with async_session_maker() as session:
            query = select(Company).where(Company.name == name)
            company = await session.execute(query)
            return company.scalars().first()
    
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
    
    @classmethod
    async def toggle_is_active(cls, name):
        async with async_session_maker() as session:
            company = await cls.get_company(name)
            query = update(Company).where(Company.name == name).values(is_active = not company.is_active)
            await session.execute(query)
            await session.commit()
            return await cls.get_company(name)
    
    @classmethod
    async def change_name(cls, name, new_name):
        async with async_session_maker() as session:
            try:
                query = update(Company).where(Company.name == name).values(name=new_name)
                await session.execute(query)
                await session.commit()
                return await cls.get_company(new_name)
            except Exception as e:
                print(type(e))
                return False
            
    @classmethod
    async def delete_company(cls, name):
        async with async_session_maker() as session:
            query = delete(Company).where(Company.name == name)
            await session.execute(query)
            await session.commit()