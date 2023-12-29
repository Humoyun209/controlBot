import json
from pprint import pprint
import aiofiles
import decimal
from aiogram import Bot, Router, F
from aiogram.types import (
    Message,
    BotCommand,
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

from filters import IsWorker
from models.user.user_dao import UserDAO
from models.user.worker_dao import WorkerDAO
from config import settings_bot


router = Router()


main_menu_workers = [
    BotCommand(command="/begin_shift", description="Начать смену"),
    BotCommand(command="/end_shift", description="Закрыть смену"),
    BotCommand(command="/cancel", description="Остановить все процессы"),
]


@router.message(Command(commands=['start']), IsWorker())
async def process_start_worker(message: Message, bot: Bot):
    await bot.set_my_commands(main_menu_workers)
    await message.answer(
        "Добро пожаловать, посмотрите на меню для управления"
    )


@router.message(Command(commands=['begin_shift']), IsWorker())
async def begin_shift_start(message: Message):
    user_id = message.from_user.id
    user = await UserDAO.get_user(user_id)
    data = await WorkerDAO.get_worker_with_companies_for_shift(user.worker.id, False)
    if data:
        keyboard = set_shift_in_company_kb(data)
        await message.answer("В какой компании хотите открыть смену",
                         reply_markup=keyboard)
    else:
        await message.answer("Компании не найдено, чтобы закончить смену /end_shift")
    

@router.callback_query(F.data.startswith("choose_company_for_begin_shift"), IsWorker())
async def choose_company_for_begin(cb: CallbackQuery):
    data = cb.data.split(":")
    worker_id, company_id = int(data[1]), int(data[2])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать смену", callback_data=f"start_begin_shift:{worker_id}:{company_id}")]
    ])
    await cb.message.answer("Чтобы начать смену нажмите на кнопку начат смену", reply_markup=keyboard)
    await cb.message.delete()


@router.callback_query(F.data.startswith("start_begin_shift:"), IsWorker())
async def start_state_for_begin_shift(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split(":")
    worker_id, company_id = int(data[1]), int(data[2])
    await state.update_data(worker_id=worker_id, company_id=company_id)
    await state.set_state(BeginShiftState.photo_group)
    await cb.message.answer(text="Пожалуйста, отправьте фото рабочего места,чашь, кальянов, каллаудов одновременно")
    await cb.message.delete()


@router.message(F.photo, IsWorker(), StateFilter(BeginShiftState.photo_group))
async def get_begin_shift_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    count_photo = data.get("count_photo")
    if count_photo is None:
        await state.update_data(count_photo=1)
        await state.update_data({f'photo1': message.photo[0].file_id})
    elif count_photo < 3:
        count_photo += 1
        await state.update_data(count_photo=count_photo)
        await state.update_data({f'photo{count_photo}': message.photo[0].file_id})
    elif count_photo == 3:
        count_photo += 1
        await state.update_data(count_photo=count_photo)
        await state.update_data({f'photo{count_photo}': message.photo[0].file_id})
        await state.set_state(BeginShiftState.grams_of_tobacco)
        await message.answer("Всё отлично!!!\nТеперь введите граммаж табаки: (В целых числах)")
    

@router.message(IsWorker(), StateFilter(BeginShiftState.grams_of_tobacco))
async def input_begin_shift_grams_tabacko(message: Message, state: FSMContext):
    grams: str = message.text
    if not grams.isdigit():
        await message.answer("Пожалуйста, введите в <b>целых числах</b>!!")
    else:
        await state.update_data(grams_of_tobacco=int(grams))
        await state.set_state(BeginShiftState.summa)
        await message.answer("Отлично!\nтепер надо ввести сумму в кассе")
        

@router.message(StateFilter(BeginShiftState.summa), IsWorker())
async def input_begin_shift_summa(message: Message, state: FSMContext):
    try:
        summa = decimal.Decimal(message.text)
        await state.update_data(summa=summa)
        begin_shift_data = await state.get_data()
        del begin_shift_data["count_photo"]
        
        await BeginShiftDAO.create_begin_shift(**begin_shift_data)
        await CompanyDAO.set_shift_to_begin(begin_shift_data.get("company_id"))
        
        await state.set_state(default_state)
        await message.answer("Смена открылась, чтобы закрыть смену /end_shift")
    except decimal.InvalidOperation:
        await message.answer("Пожалуйста, отправьте в виде числа - например: 1000, 10500, 100000")
