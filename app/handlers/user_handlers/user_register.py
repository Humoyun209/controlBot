from aiogram import Bot, Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from models.enums import UserStatus
from keyboards.users_kb import register_user_kb

from models.user.user_dao import UserDAO
from states.non_register_state import NoneRegisterState


router = Router()

contact_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Отправить номер телефона", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


@router.message(Command(commands=["start"]))
async def get_none_register_user(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    await state.update_data(id=user_id, username=username)
    await state.set_state(NoneRegisterState.phone)
    await message.answer("Пожалуйста отправьте свой телефон: ", reply_markup=contact_kb)


@router.message(F.contact, StateFilter(NoneRegisterState.phone))
async def get_contact_from_user(message: Message, bot: Bot, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    data = await state.get_data()
    admin = await UserDAO.get_super_admin()
    keyboard = register_user_kb(**data)
    await bot.send_message(
        chat_id=admin.id,
        text=f"""Новый пользователь\nID: {data.get('id')}\nUsername: {data.get('username')}\nPhone: {data.get('phone')}""",
        reply_markup=keyboard,
    )
    await message.answer("Спасибо, ждите сообщение админа")
    await state.set_data(default_state)


@router.message(StateFilter(NoneRegisterState.phone))
async def get_contact_error(message: Message):
    await message.answer(
        text="Кажется, вы не правильно отправили номер телефона, отправите повторно",
        reply_markup=contact_kb,
    )


@router.callback_query(F.data.startswith("activate_none_user:"))
async def activate_none_user(cb: CallbackQuery, bot: Bot):
    data = cb.data.split(":")
    await UserDAO.create_user(**{
            'id': int(data[1]),
            'username': data[2],
            'phone': data[3],
            'status': UserStatus.USER
        }
    )
    await cb.message.answer('Пользователь активирован!')
    await cb.message.delete()
    await bot.send_message(int(data.get("id")), text="Админ вас активировал!!!")
    

@router.callback_query(F.data.startswith("remove_none_user:"))
async def remove_none_user(cb: CallbackQuery, bot: Bot):
    data = cb.data.split(":")
    user_id = int(data[1])
    await cb.message.answer(text="Пользователь игнорирован!")
    await cb.message.delete()
    await bot.send_message(user_id, "Админ вас игнорировал!!!")
