from aiogram import Bot, Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.filters import Command
from models.user.models import UserStatus

from filters import IsUser
from models.user.user_dao import UserDAO
from config import settings_bot


router = Router()


@router.message(Command(commands=['start']), IsUser())
async def process_start_user(message: Message):
    await message.answer("You are - Worker")


@router.message(Command(commands=['start']))
async def process_start_user(message: Message, bot: Bot):
    await UserDAO.create_user(
        message.from_user.id,
        message.from_user.username,
        UserStatus.ANONYMOUS
    )
    await bot.send_message(
        settings_bot.admin_id,
        f"✅ Новый пользователь\n\n<b><i>ID: </i></b>{message.from_user.id}<b><i>\nUsername:</i></b> {message.from_user.username}"
    )
    await message.answer("You are - Anonymous Worker")