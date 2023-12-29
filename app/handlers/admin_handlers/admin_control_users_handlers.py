from aiogram import Bot, Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
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
    admin_actions_kb,
    admin_users_kb,
    hookah_actions_kb,
    hookah_users_kb,
    regular_users_kb,
    user_actions_kb,
    toggle_worker_from_company_kb,
    get_user_manage_kb,
)


router = Router()


is_admin = or_f(IsAdmin(), IsSuperAdmin())


@router.message(Command(commands=["users"]), or_f(IsAdmin(), IsSuperAdmin()))
async def get_started_users(message: Message):
    await message.answer(
        "Пожалуйста, выберите действие:",
        reply_markup=get_user_manage_kb(is_super=IsSuperAdmin(message.from_user.id)),
    )


@router.callback_query(F.data.startswith("to_worker_user_manage"), is_admin)
async def get_worker_manage(cb: CallbackQuery):
    workers = await UserDAO.get_workers()
    if len(workers) > 0:
        keyboard = hookah_users_kb(workers)
        await cb.message.answer(
            "Выберите действие для кальяншиков", reply_markup=keyboard
        )
    else:
        await cb.message.answer("Кальяншики не найдены!!!")
    await cb.message.delete()


@router.callback_query(F.data.startswith("to_what_user_manage"), is_admin)
async def get_worker_manage(cb: CallbackQuery):
    users = await UserDAO.get_users()
    if len(users) > 0:
        keyboard = regular_users_kb(users)
        await cb.message.answer(
            "Выберите действие для пользователей", reply_markup=keyboard
        )
    else:
        await cb.message.answer("Юзеры не найдены!!!")
    await cb.message.delete()


@router.callback_query(F.data.startswith("to_admin_user_manage"), IsSuperAdmin())
async def get_worker_manage(cb: CallbackQuery):
    admins = await UserDAO.get_admins()
    if len(admins) > 0:
        keyboard = admin_users_kb(admins)
        await cb.message.answer(
            "Выберите действие для кальяншиков", reply_markup=keyboard
        )
    else:
        await cb.message.answer("Админы не найдены!!!")
    await cb.message.delete()


@router.callback_query(F.data.startswith("hookah_to_actions:"), is_admin)
async def get_worker_user_manage(cb: CallbackQuery):
    user_id = int(cb.data.split(":")[1])
    await cb.message.answer(
        "Выберите действие: ", reply_markup=hookah_actions_kb(user_id)
    )
    await cb.message.delete()


@router.callback_query(F.data.startswith("user_to_actions:"), is_admin)
async def get_regular_user_manage(cb: CallbackQuery):
    user_id = int(cb.data.split(":")[1])
    await cb.message.answer(
        "Выберите действие: ", reply_markup=user_actions_kb(user_id)
    )
    await cb.message.delete()


@router.callback_query(F.data.startswith("admin_to_actions:"), IsSuperAdmin())
async def get_admin_user_manage(cb: CallbackQuery):
    user_id = int(cb.data.split(":")[1])
    await cb.message.answer(
        "Выберите действие: ", reply_markup=admin_actions_kb(user_id)
    )
    await cb.message.delete()


@router.callback_query(F.data.startswith("to_worker_user_manage"), is_admin)
async def get_admin_manage(cb: CallbackQuery):
    workers = await UserDAO.get_workers()
    keyboard = hookah_users_kb(workers)
    await cb.message.answer("Выберите действие для кальяншиков", reply_markup=keyboard)


@router.callback_query(F.data.startswith("user_to_actions"), is_admin)
async def anonym_user_actions(cb: CallbackQuery):
    user_id = int(cb.data.split(":")[1])

    keyboard = user_actions_kb(user_id)
    await cb.message.answer(
        "Пожалуйста выберите, что хотите делать с пользователем: ",
        reply_markup=keyboard,
    )
    await cb.message.delete()


@router.callback_query(F.data.startswith("user_delete"), IsSuperAdmin())
async def delete_user(cb: CallbackQuery):
    user_id = int(cb.data.split(":")[1])
    await UserDAO.delete_user(user_id)
    await cb.message.answer("Пользователь удален!!!")
    await cb.message.answer()


@router.callback_query(F.data.startswith("admin_status_change"), IsSuperAdmin())
async def change_admin_status(cb: CallbackQuery):
    user_id = int(cb.data.split(":")[1])
    await UserDAO.update_user(user_id, status=UserStatus.USER)
    await cb.message.answer(f"Статус юзера с ID = {user_id}\nИзменен на USER")
    await cb.message.delete()


@router.callback_query(F.data.startswith("user_invite_companies:"), is_admin)
async def anonym_user_invite_companies(cb: CallbackQuery):
    user_id = int(cb.data.split(":")[1])
    worker = await WorkerDAO.worker_create(user_id)
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
