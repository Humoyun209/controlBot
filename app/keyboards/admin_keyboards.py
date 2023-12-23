from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import KeyboardBuilder, InlineKeyboardBuilder

from models.company.models import Company


manage_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="✅ Создать новую компанию", callback_data="company:create")
    ],
    [
        InlineKeyboardButton(text="📃 Список компаний", callback_data="company:list"),
        InlineKeyboardButton(text='🔙 Главная', callback_data='TO_HOME_ADMIN')
    ]
])


def get_companies_list_kb(companies: list[Company]):
    builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardBuilder] = [
        InlineKeyboardButton(text=company.name, callback_data=f"company_item:{company.name}")
        for company in companies
    ]
    builder.row(*buttons, width=1)
    builder.add(InlineKeyboardButton(text='🔙 Главная', callback_data='TO_HOME_ADMIN'))
    return builder.as_markup()


def company_manage_kb(company: Company):
    active_text = "✅ Работает" if company.is_active else "❌ Не работает"
    view_map = InlineKeyboardButton(text="👁‍🗨 Техническая карта заведения", callback_data=f"company_view_technical_map:{company.name}")
    change_name = InlineKeyboardButton(text="📝 Изменить имя", callback_data=f"company_change_name:{company.name}")
    change_active = InlineKeyboardButton(text=active_text, callback_data=f"company_change_is_active:{company.name}")
    delete_btn = InlineKeyboardButton(text="❌ Удалить", callback_data=f"company_delete:{company.name}")
    back = InlineKeyboardButton(text='🔙 Главная', callback_data='TO_HOME_ADMIN')
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [change_name, change_active],
        [view_map],
        [delete_btn],
        [back],
    ])
    
    return keyboard
    