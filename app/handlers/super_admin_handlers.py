from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
)
from aiogram.filters import Command, or_f, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from models.user.user_dao import UserDAO


from filters import IsSuperAdmin


router = Router()
    

@router.message(Command(commands=['cancel']), ~StateFilter(default_state))
async def cancel_all_process(message: Message, state: FSMContext):
    await message.answer("Вы остановили все процессы, которые запушены")
    await state.set_state(default_state)


@router.message(Command(commands=['cancel']))
async def cancel_error(message: Message):
    await message.answer("Никакой процесс не запушен")
    

@router.callback_query(F.data.startswith("user_to_admin:"), IsSuperAdmin())
async def create_simple_admin(cb: CallbackQuery):
    user_id = int(cb.data.split(":")[1])
    await UserDAO.appoint_as_admin(user_id)
    await cb.message.answer(f"Пользователь ID - {user_id} назначен админом")
    await cb.message.delete()


