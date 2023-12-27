import json
from pprint import pprint
import aiofiles
import decimal
from aiogram import Bot, Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from keyboards.shift_kb import set_shift_in_company_kb
from models.user.models import UserStatus
from states.shift import BeginShiftState
from models.company.begin_shift_dao import BeginShiftDAO
from models.company.company_dao import CompanyDAO

from filters import IsUser
from models.user.user_dao import UserDAO, WorkerDAO
from config import settings_bot


router = Router()


@router.message(Command(commands=['end_shift']), IsUser())
async def end_shift_start(message: Message):
    user_id = message.from_user.id
    user = await UserDAO.get_user(user_id)
    data = await WorkerDAO.get_worker_with_companies_for_shift(worker_id=user.worker.id, live=True)
    if data:
        keyboard = set_shift_in_company_kb(data, begin=False)
        await message.answer("В какой компании хотите закрыть смену",
                            reply_markup=keyboard)
    else:
        await message.answer("Компании не найдено, чтобы закончить смену /begin_shift")
   

@router.callback_query(F.data.startswith("choose_company_for_end_shift"), IsUser())
async def choose_company_for_end_shift(cb: CallbackQuery):
    data = cb.data.split(":")
    worker_id, company_id = int(data[1]), int(data[2])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Закрыть смену", callback_data=f"start_end_shift:{worker_id}:{company_id}")]
    ])
    await cb.message.answer("Чтобы начать смену нажмите на кнопку начат смену", reply_markup=keyboard)
    await cb.message.delete()