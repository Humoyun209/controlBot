from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import KeyboardBuilder, InlineKeyboardBuilder
from models.enums import UserStatus
from models.user.models import Worker
from models.user.models import User

from models.company.models import Company


BACK_BUTTON = InlineKeyboardButton(text='🔙 Главная', callback_data='TO_HOME_ADMIN')


users_manage_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Управление пользователями", callback_data="user_worker_manage")],
    [InlineKeyboardButton(text="Новые ползователи", callback_data="anonym_to_user")],
    [BACK_BUTTON]
])


def users_list_kb(anonym_users: list[User]):
    builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    for user in anonym_users:
        buttons.append(
            InlineKeyboardButton(
                text=f"{user.username} | {user.phone} | {'Аноним' if user.status == UserStatus.ANONYMOUS else 'Пользователь'}", 
                callback_data=f"user_to_actions: {user.id}"
            )
        )
    buttons.append(BACK_BUTTON)
    builder = builder.row(*buttons, width=1)
    return builder.as_markup()


def user_actions_kb(user_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить в компании", callback_data=f"user_invite_companies:{user_id}")],
        [InlineKeyboardButton(text="Удалить пользователя", callback_data=f"user_delete:{user_id}")],
        [InlineKeyboardButton(text="Назначить админом", callback_data=f"user_to_admin:{user_id}")],
        [BACK_BUTTON],
    ])
    
    return keyboard


def toggle_worker_from_company_kb(worker: Worker, company_list: list[Company]):
    builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    buttons.append(InlineKeyboardButton(text="Удалить пользователя", callback_data=f"delete_worker:{worker.id}"))
    for company in company_list:
        buttons.append(
            InlineKeyboardButton(
                text=f'Удалить из "{company.name}"' if worker in company.workers else f'Добавить в "{company.name}"', 
                callback_data=f"user_manage_company:{company.name}:{worker.id}"
            )
        )
    buttons.append(BACK_BUTTON)
    builder = builder.row(*buttons, width=1)
    return builder.as_markup()


def get_users_kb(users: list[User]):
    builder = InlineKeyboardBuilder()
    buttons = []
    for user in users:
        btn = InlineKeyboardButton(
            text=f"{user.username}  |  {user.phone}  |  {'admin' if UserStatus.ADMIN == user.status else 'user'}",
            callback_data=f"active_user_{'admin' if UserStatus.ADMIN == user.status else 'user'}:{user.id}"
        )
        buttons.append(btn)
    buttons.append(BACK_BUTTON)
    builder = builder.row(*buttons, width=1)
    return builder.as_markup()
