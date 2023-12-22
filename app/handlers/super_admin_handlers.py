from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.filters import Command


from filters import IsSuperAdmin

router = Router()

@router.message(Command(commands=['start']), IsSuperAdmin())
async def process_start_user(message: Message):
    await message.answer("You are - Super Admin")