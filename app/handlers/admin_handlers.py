from aiogram import Bot, Router, F
from aiogram.types import (
    Message,
    BotCommand,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.filters import Command, StateFilter, or_f, and_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from models.user.user_dao import UserDAO, WorkerDAO
from lexicon import ADMINS
from models.company.company_dao import CompanyDAO
from models.enums import UserStatus
from filters import IsAdmin, IsSuperAdmin
from keyboards.company_kb import (
    company_main_kb,
    company_management_kb,
    get_companies_list_kb,
)
from keyboards.users_kb import (
    user_actions_kb,
    users_list_kb,
    toggle_worker_from_company_kb,
    users_manage_kb,
)
from states.company import ChangeCompany, CreateCompany

router = Router()

is_admin = or_f(IsAdmin(), IsSuperAdmin())

main_menu_admins = [
    BotCommand(command="/company", description="Для управления компаний"),
    BotCommand(command="/users", description="Для управления пользователей"),
    BotCommand(command="/reports", description="Отчёты"),
]


@router.message(Command(commands=["start"]), IsAdmin())
async def process_start_user(message: Message, bot: Bot):
    await bot.set_my_commands(main_menu_admins)
    await message.answer("You are - Admin")


@router.callback_query(
    F.data.startswith("TO_HOME"),
    or_f(~StateFilter(default_state), StateFilter(default_state)),
)
async def to_home_baby(cb: CallbackQuery, state: FSMContext):
    await state.set_state(default_state)
    await cb.message.delete()


@router.message(Command(commands=["company"]), or_f(IsAdmin(), IsSuperAdmin()))
async def manage_company(message: Message, bot: Bot):
    await bot.set_my_commands(main_menu_admins)
    await message.answer(
        text="Здесь вы можете управлять компаниями",
        reply_markup=company_main_kb,
    )


# ========================== Хендлеры для создания компанию ===============================#


@router.callback_query(
    F.data.startswith("company:create"),
    or_f(IsAdmin(), IsSuperAdmin()),
    StateFilter(default_state),
)
async def create_company_start(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer("Введите, имя новую компанию")
    await cb.message.delete()
    await state.set_state(CreateCompany.name)


@router.message(or_f(IsAdmin(), IsSuperAdmin()), StateFilter(CreateCompany.name))
async def create_company_in_db(message: Message, state: FSMContext):
    company_name = message.text
    company = await CompanyDAO.get_company(company_name)
    if company is None:
        await state.update_data(name=company_name)
        await state.set_state(CreateCompany.technical_map)
        await message.answer(
            "Спасибо,\nтепер введите техническую карту компании в виде файла"
        )
    else:
        await message.answer(
            "Пожалуй,\nc таким именем компания имеется.\nВведите заново"
        )


@router.message(
    F.document,
    or_f(IsAdmin(), IsSuperAdmin()),
    StateFilter(CreateCompany.technical_map),
)
async def create_technical_map(message: Message, state: FSMContext):
    f = message.document.file_id
    await state.update_data(technical_map=f)
    new_company = await state.get_data()
    await CompanyDAO.create_company(**new_company)
    await state.set_state(default_state)
    await message.answer("Спасибо, чтобы возврашаться нажмите на /company")


# ========================== Хендлер для список компаний ===============================#


@router.callback_query(
    F.data == "company:list",
    or_f(IsAdmin(), IsSuperAdmin()),
    StateFilter(default_state),
)
async def company_list(cb: CallbackQuery):
    companies = await CompanyDAO.list_company()
    keyboard = get_companies_list_kb(companies)
    await cb.message.answer("<b>Список компаний:</b>", reply_markup=keyboard)
    await cb.message.delete()


@router.callback_query(
    F.data.startswith("company_item:"), or_f(IsAdmin(), IsSuperAdmin())
)
async def company_manage(cb: CallbackQuery):
    company_name = cb.data.split(":")[1].strip()
    company = await CompanyDAO.get_company(company_name)
    keyboard = company_management_kb(company)
    await cb.message.answer(
        f"<b><i>Компания: </i></b>{company.name}\nВыберите действие:",
        reply_markup=keyboard,
    )
    await cb.message.delete()


# ========================= Company CRUD ===========================#


@router.callback_query(
    F.data.startswith("company_change_is_active"), or_f(IsAdmin(), IsSuperAdmin())
)
async def company_change_is_active(cb: CallbackQuery):
    company_name = cb.data.split(":")[1].strip()
    company = await CompanyDAO.toggle_is_active(company_name)
    keyboard = company_management_kb(company)
    await cb.message.answer(
        f"<b><i>Компания: </i></b>{company.name}\nВыберите действие:",
        reply_markup=keyboard,
    )
    await cb.message.delete()


@router.callback_query(
    F.data.startswith("company_change_name"), or_f(IsAdmin(), IsSuperAdmin())
)
async def company_name_(cb: CallbackQuery, state: FSMContext):
    company_name = cb.data.split(":")[1].strip()
    await cb.message.answer(f"Введите новое имя: ")
    await state.update_data(name=company_name)
    await state.set_state(ChangeCompany.name)
    await cb.message.delete()


@router.message(or_f(IsAdmin(), IsSuperAdmin()), StateFilter(ChangeCompany.name))
async def company_change_name(message: Message, state: FSMContext):
    data = await state.get_data()
    company_name = data.get("name")
    company = await CompanyDAO.change_name(company_name, message.text)
    if company:
        await state.set_state(default_state)
        keyboard = company_management_kb(company)
        await message.answer(
            f"<b><i>Компания: </i></b>{company.name}\nВыберите действие:",
            reply_markup=keyboard,
        )
    else:
        await message.answer("Похоже, компания с таким именем имеется, введите заново")


@router.callback_query(
    F.data.startswith("company_delete:"), or_f(IsAdmin(), IsSuperAdmin())
)
async def delete_company(cb: CallbackQuery):
    company_name = cb.data.split(":")[1].strip()
    await CompanyDAO.delete_company(company_name)
    await cb.message.answer(ADMINS.get("main"))
    await cb.message.delete()


@router.callback_query(
    F.data.startswith("company_view_technical_map"), or_f(IsAdmin(), IsSuperAdmin())
)
async def company_change_is_active(cb: CallbackQuery):
    company_name = cb.data.split(":")[1].strip()
    company = await CompanyDAO.get_company(company_name)
    await cb.message.answer_document(
        company.technical_map, caption=f"Техническая карта - {company.name}"
    )


# ============================= Управление юзерами ================================ #


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
        "Пожалуйста выберите, что хотите делать пользователем: ", reply_markup=keyboard
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
