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

from models.user.user_dao import UserDAO
from models.user.worker_dao import WorkerDAO
from lexicon import ADMINS
from models.company.company_dao import CompanyDAO
from models.enums import UserStatus
from filters import IsAdmin, IsSuperAdmin
from keyboards.company_kb import (
    company_main_kb,
    company_management_kb,
    get_companies_list_kb,
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
    await message.answer(
        text="Здесь вы можете управлять компаниями",
        reply_markup=company_main_kb,
    )


@router.callback_query(
    F.data.startswith("company:create"),
    or_f(IsAdmin(), IsSuperAdmin()),
    StateFilter(default_state),
)
async def create_company_start(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer("Введите, имя новую компанию")
    await cb.message.delete()
    await state.set_state(CreateCompany.name)


@router.message(is_admin, StateFilter(CreateCompany.name))
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
