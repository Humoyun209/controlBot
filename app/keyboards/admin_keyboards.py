from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import KeyboardBuilder, InlineKeyboardBuilder

from models.company.models import Company


inline_keyboard = [
    [
        InlineKeyboardButton(text="✅ Создать новую компанию", callback_data="company:create"),
    ],
    [
        InlineKeyboardButton(text="📃 Список компаний", callback_data="company:list"),
    ]
]

manage_kb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def get_companies_list_kb(companies: list[Company]):
    builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardBuilder] = [
        InlineKeyboardButton(text=company.name, callback_data=f"company_item:{company.id}")
        for company in companies
    ]
    return builder.row(*buttons, width=1).as_markup()