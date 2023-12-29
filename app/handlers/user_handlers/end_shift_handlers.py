import decimal
from aiogram import Bot, Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State
from models.company.end_shift_dao import EndShiftDAO

from keyboards.shift_kb import set_shift_in_company_kb
from states.shift import EndShiftState
from models.company.begin_shift_dao import BeginShiftDAO
from models.company.company_dao import CompanyDAO

from filters import IsUser
from models.user.user_dao import UserDAO
from models.user.worker_dao import WorkerDAO
from config import settings_bot


router = Router()


async def shortcut_for_int_numbers_input(
    message: Message,
    state: FSMContext,
    next_state: State,
    update_attr_name: str,
    message_for_next: str,
):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите в <b>целых числах</b>!!")
    else:
        await state.update_data(**{update_attr_name: int(message.text)})
        await state.set_state(next_state)
        await message.answer(message_for_next)


@router.message(Command(commands=["end_shift"]), IsUser())
async def end_shift_start(message: Message):
    user_id = message.from_user.id
    user = await UserDAO.get_user(user_id)
    data = await WorkerDAO.get_worker_with_companies_for_shift(
        worker_id=user.worker.id, live=True
    )
    if data:
        keyboard = set_shift_in_company_kb(data, begin=False)
        await message.answer(
            "В какой компании хотите закрыть смену", reply_markup=keyboard
        )
    else:
        await message.answer("Компании не найдено, чтобы начать смену /begin_shift")


@router.callback_query(F.data.startswith("choose_company_for_end_shift"), IsUser())
async def choose_company_for_end_shift(cb: CallbackQuery):
    data = cb.data.split(":")
    worker_id, company_id = int(data[1]), int(data[2])
    begin_shift = await BeginShiftDAO.get_last_begin_shift_for_company_and_worker(
        company_id, worker_id
    )
    if not begin_shift:
        await cb.message.answer("Произошло ошибка!!! Начальная смена не найдена")
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Закрыть смену",
                        callback_data=f"start_end_shift:{worker_id}:{company_id}:{begin_shift.id}",
                    )
                ]
            ]
        )
        await cb.message.answer(
            "Чтобы начать смену нажмите на кнопку начат смену", reply_markup=keyboard
        )
        await cb.message.delete()


@router.callback_query(F.data.startswith("start_end_shift"))
async def start_end_shift_ready(cb: CallbackQuery, state: FSMContext):
    data = cb.data.split(":")
    worker_id, company_id, begin_shift_id = int(data[1]), int(data[2]), int(data[3])
    await state.update_data(
        worker_id=worker_id, company_id=company_id, begin_shift_id=begin_shift_id
    )
    await state.set_state(EndShiftState.photo_group)
    await cb.message.answer("Отправьте 4 фото кассы одновременно")
    await cb.message.delete()


@router.message(F.photo, IsUser(), StateFilter(EndShiftState.photo_group))
async def get_end_shift_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    print(data)
    count_photo = data.get("count_photo")
    if count_photo is None:
        await state.update_data(count_photo=1)
        await state.update_data({f"photo1": message.photo[0].file_id})
    elif count_photo < 3:
        count_photo += 1
        await state.update_data(count_photo=count_photo)
        await state.update_data({f"photo{count_photo}": message.photo[0].file_id})
    elif count_photo == 3:
        count_photo += 1
        await state.update_data(count_photo=count_photo)
        await state.update_data({f"photo{count_photo}": message.photo[0].file_id})
        await state.set_state(EndShiftState.grams_of_tobacco)
        await message.answer(
            "Всё отлично!!!\nТеперь введите граммаж табаки: (В целых числах)"
        )


@router.message(IsUser(), StateFilter(EndShiftState.grams_of_tobacco))
async def input_end_shift_grams_tabacko(message: Message, state: FSMContext):
    grams: str = message.text
    if not grams.isdigit():
        await message.answer("Пожалуйста, введите в <b>целых числах</b>!!")
    else:
        await state.update_data(grams_of_tobacco=int(grams))
        await state.set_state(EndShiftState.summa)
        await message.answer("Отлично!\nтепер надо ввести сумму в кассе")


@router.message(StateFilter(EndShiftState.summa), IsUser())
async def input_begin_shift_summa(message: Message, state: FSMContext):
    try:
        summa = decimal.Decimal(message.text)
        await state.update_data(summa=summa)
        await state.set_state(EndShiftState.quantity_of_sold)
        await message.answer("Круто, введите сколько кальянов ппроданы: ")
    except decimal.InvalidOperation:
        await message.answer(
            "Пожалуйста, отправьте в виде числа - например: 1000, 10500, 100000"
        )


@router.message(StateFilter(EndShiftState.quantity_of_sold), IsUser())
async def input_quantity_of_sold_end_shift(message: Message, state: FSMContext):
    await shortcut_for_int_numbers_input(
        message=message,
        state=state,
        next_state=EndShiftState.promo_quantity,
        update_attr_name='quantity_of_sold',
        message_for_next="Отлично!!!\nВведите к-во проданных промо кальянов"
    )


@router.message(StateFilter(EndShiftState.promo_quantity), IsUser())
async def input_quantity_promo_end_shift(message: Message, state: FSMContext):
    await shortcut_for_int_numbers_input(
        message=message,
        state=state,
        next_state=EndShiftState.card,
        update_attr_name='promo_quantity',
        message_for_next="Отлично!!!\nВведите к-во проданных кальянов картой"
    )


@router.message(StateFilter(EndShiftState.card), IsUser())
async def input_quantity_card_end_shift(message: Message, state: FSMContext):
    await shortcut_for_int_numbers_input(
        message=message,
        state=state,
        next_state=EndShiftState.cash,
        update_attr_name='card',
        message_for_next="Отлично!!!\nВведите к-во проданных кальянов налычными"
    )


@router.message(StateFilter(EndShiftState.cash), IsUser())
async def input_quantity_cash_end_shift(message: Message, state: FSMContext):
    await shortcut_for_int_numbers_input(
        message=message,
        state=state,
        next_state=EndShiftState.in_club,
        update_attr_name='cash',
        message_for_next="Отлично!!!\nВведите к-во проданных кальянов в клубе"
    )
    

@router.message(StateFilter(EndShiftState.in_club), IsUser())
async def input_quantity_in_club_end_shift(message: Message, state: FSMContext):
    await shortcut_for_int_numbers_input(
        message=message,
        state=state,
        next_state=EndShiftState.in_club_card,
        update_attr_name='in_club',
        message_for_next="Отлично!!!\nСколько кальянов оплачено картой в клубе?"
    )
    
    
@router.message(StateFilter(EndShiftState.in_club_card), IsUser())
async def input_quantity_promo_in_club_card_end_shift(message: Message, state: FSMContext):
    await shortcut_for_int_numbers_input(
        message=message,
        state=state,
        next_state=EndShiftState.in_club_cash,
        update_attr_name='in_club_card',
        message_for_next="Отлично!!!\nВведите к-во проданных кальянов в клубе налычными"
    )
    

@router.message(StateFilter(EndShiftState.in_club_cash), IsUser())
async def input_quantity_in_club_cash_end_shift(message: Message, state: FSMContext):
    await shortcut_for_int_numbers_input(
        message=message,
        state=state,
        next_state=EndShiftState.tips,
        update_attr_name='in_club_cash',
        message_for_next="Отлично!!!\nСколько чаевых оставили на карту?"
    )
    

@router.message(StateFilter(EndShiftState.tips), IsUser())
async def input_sum_tips_end_shift(message: Message, bot: Bot, state: FSMContext):
    try:
        tips = decimal.Decimal(message.text)
        await state.update_data(tips=tips)
        await state.set_state(default_state)
        data = await state.get_data()
        del data["count_photo"]
        end_shift = await EndShiftDAO.create_end_shift(**data)
        await CompanyDAO.set_shift_to_end(data.get('company_id'))
        
        # Отправить сообщение админу
        company = await CompanyDAO.get_company_by_id(end_shift.company_id)
        worker = await WorkerDAO.get_worker_by_id(end_shift.worker_id)
        super_admin = await UserDAO.get_super_admin()
        photos = [end_shift.photo1, end_shift.photo2, end_shift.photo3, end_shift.photo4]
        for i, photo in enumerate(photos):
            if i == 3:
                await bot.send_photo(
                super_admin.id,
                photo, 
                caption=f"""
Смена закрылась!!!
Дата: {end_shift.created.isoformat()}
Название заведения: {company.name}
Граммаж табака: {end_shift.grams_of_tobacco}
Работник: {worker.user.username}
"""
            )
            await bot.send_photo(
                super_admin.id,
                photo
            )
        await message.answer("Смена закрылась, чтобы открыть смену /begin_shift")
    except decimal.InvalidOperation:
        await message.answer(
            "Пожалуйста, отправьте в виде числа - например: 1000, 10500, 100000"
        )
