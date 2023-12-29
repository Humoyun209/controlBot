from aiogram import Bot, Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.filters import Command, StateFilter, or_f, and_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from models.user.user_dao import UserDAO
from models.user.worker_dao import WorkerDAO
from lexicon import ADMINS
from models.company.company_dao import CompanyDAO
from models.enums import UserStatus
from filters import IsAdmin, IsSuperAdmin
from keyboards.users_kb import (
    user_actions_kb,
    users_list_kb,
    toggle_worker_from_company_kb,
    users_manage_kb,
)
from states.company import ChangeCompany, CreateCompany


router = Router()

is_admin = or_f(IsAdmin(), IsSuperAdmin())


@router.message(Command(commands=["users"]), or_f(IsAdmin(), IsSuperAdmin()))
async def get_started_users(message: Message):
    await message.answer("Пожалуйста, выберите действие:", reply_markup=users_manage_kb)


@router.callback_query(F.data == "user_worker_manage", is_admin)
async def get_user_list(cb: CallbackQuery):
    anonym_users = await UserDAO.get_users_without_anonyms()
    keyboard = users_list_kb(anonym_users)
    await cb.message.answer("Список новых пользователей: ", reply_markup=keyboard)
    await cb.message.delete()


@router.callback_query(F.data.startswith("user_to_actions"), is_admin)
async def anonym_user_actions(cb: CallbackQuery):
    user_id = int(cb.data.split(":")[1])
    
    keyboard = user_actions_kb(user_id)
    await cb.message.answer(
        "Пожалуйста выберите, что хотите делать с пользователем: ", reply_markup=keyboard
    )
    await cb.message.delete()


@router.callback_query(F.data.startswith("user_invite_companies:"), is_admin)
async def anonym_user_invite_companies(cb: CallbackQuery):
    user_id = int(cb.data.split(":")[1])
    worker = await WorkerDAO.worker_create(user_id)
    print(worker, user_id)
    await UserDAO.change_user_status(user_id, UserStatus.USER)
    company_list = await CompanyDAO.get_list_with_workers()
    keyboard = toggle_worker_from_company_kb(worker, company_list)
    await cb.message.answer(
        "Вы можете добавить / удалить работника в компанию",
        reply_markup=keyboard,
    )
    await cb.message.delete()


@router.callback_query(F.data.startswith("user_manage_company:"), is_admin)
async def toggle_worker_company(cb: CallbackQuery):
    lst = cb.data.split(":")
    company_name = lst[1].strip()
    worker_id = int(lst[2].strip())
    await WorkerDAO.toggle_company_to_worker(worker_id, company_name)
    worker = await WorkerDAO.get_worker_by_id(worker_id)
    company_list = await CompanyDAO.get_list_with_workers()
    keyboard = toggle_worker_from_company_kb(worker, company_list)
    await cb.message.answer(
        "Вы можете добавить / удалить работника в компанию",
        reply_markup=keyboard,
    )
    await cb.message.delete()
