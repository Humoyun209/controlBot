from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import KeyboardBuilder, InlineKeyboardBuilder

from models.company.models import Company

from models.user.models import User, Worker


BACK_BUTTON = InlineKeyboardButton(text='🔙 Главная', callback_data='TO_HOME_ADMIN')


def set_shift_in_company_kb(data: list[tuple[int, str]], begin=True):
    builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []
    for worker_id, company_id, company_name in data:
        buttons.append(
            InlineKeyboardButton(
                text=f"{company_name}",
                callback_data=f"choose_company_for_{'begin' if begin else 'end'}_shift:{worker_id}:{company_id}",
            )
        )
    buttons.append(BACK_BUTTON)
    builder = builder.row(*buttons, width=1)
    return builder.as_markup()
