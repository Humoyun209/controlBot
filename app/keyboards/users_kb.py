from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import KeyboardBuilder, InlineKeyboardBuilder
from filters import IsWorker, IsUser, IsAdmin
from models.enums import UserStatus
from models.user.models import Worker
from models.user.models import User

from models.company.models import Company


BACK_BUTTON = InlineKeyboardButton(text='🔙 Главная', callback_data='TO_HOME_ADMIN')


def get_user_manage_kb(is_super: bool):
    builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(text="Кальяншики", callback_data="to_worker_user_manage"),
        InlineKeyboardButton(text="Недавно активитированные и юзеры", callback_data="to_what_user_manage"),
    ]
    if is_super:
        buttons.append(InlineKeyboardButton(text="Админы", callback_data="to_admin_user_manage"))
    buttons.append(BACK_BUTTON)
    builder.row(*buttons, width=1)
    return builder.as_markup()


def users_list_kb(users: list[User], prefix: str):
    builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    for user in users:
        buttons.append(
            InlineKeyboardButton(
                text=f"{user.username} - {user.phone}", 
                callback_data=f"{prefix}:{user.id}"
            )
        )
    buttons.append(BACK_BUTTON)
    builder = builder.row(*buttons, width=1)
    return builder.as_markup()


def hookah_users_kb(users):
    return users_list_kb(users, "hookah_to_actions")


def regular_users_kb(users):
    return users_list_kb(users, "user_to_actions")


def admin_users_kb(users):
    return users_list_kb(users, "admin_to_actions")


def admin_actions_kb(user_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить статус на юзер", callback_data=f"admin_status_change:{user_id}")],
        [InlineKeyboardButton(text="Удалить админа", callback_data=f"user_delete:{user_id}")],
        [BACK_BUTTON],
    ])
    return keyboard


def hookah_actions_kb(user_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить в компании", callback_data=f"user_invite_companies:{user_id}")],
        [InlineKeyboardButton(text="Удалить пользователя", callback_data=f"user_delete:{user_id}")],
        [BACK_BUTTON],
    ])
    return keyboard


def user_actions_kb(user_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Добавить в компании", callback_data=f"user_invite_companies:{user_id}")],
        [InlineKeyboardButton(text="Назначить админом", callback_data=f"user_to_admin:{user_id}")],
        [InlineKeyboardButton(text="Удалить пользователя", callback_data=f"user_delete:{user_id}")],
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


def register_user_kb(**data):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Активировать пользователя", callback_data=f"activate_none_user:{data.get('id')}:{data.get('username')}:{data.get('phone')}")],
        [InlineKeyboardButton(text="Удалить пользователя", callback_data=f"remove_none_user:{data.get('user_id')}")],
    ])
    return keyboard