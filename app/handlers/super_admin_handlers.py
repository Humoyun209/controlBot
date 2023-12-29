from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
)
from aiogram.filters import Command
from models.user.user_dao import UserDAO


from filters import IsSuperAdmin


router = Router()


@router.message(Command(commands=['start']), IsSuperAdmin())
async def process_start_user(message: Message):
    await message.answer("You are - Super Admin")
    

@router.callback_query(F.data.startswith("user_to_admin:"), IsSuperAdmin())
async def create_simple_admin(cb: CallbackQuery):
    user_id = int(cb.data.split(":")[1])
    await UserDAO.appoint_as_admin(user_id)
    await cb.message.answer(f"Пользователь ID - {user_id} назначен админом")
    await cb.message.delete()


