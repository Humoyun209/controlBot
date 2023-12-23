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
from models.company.company_dao import CompanyDAO

from filters import IsAdmin, IsSuperAdmin
from keyboards.admin_keyboards import get_companies_list_kb, manage_kb
from states.company import CreateCompany

router = Router()


main_menu_admins = [
    BotCommand(command="/company", description="Для управления компаний"),
    BotCommand(command="/users", description="Для управления пользователей"),
    BotCommand(command="/reports", description="Отчёты"),
]


@router.message(Command(commands=["start"]), IsAdmin())
async def process_start_user(message: Message, bot: Bot):
    await bot.set_my_commands(main_menu_admins)
    await message.answer("You are - Admin")


@router.message(Command(commands=["company"]), or_f(IsAdmin(), IsSuperAdmin()))
async def manage_company(message: Message, bot: Bot):
    await bot.set_my_commands(main_menu_admins)
    await message.answer(
        text="Чтобы создать новую компанию, нажмите на эту кнопку",
        reply_markup=manage_kb,
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
async def create_company(message: Message, state: FSMContext):
    company_name = message.text
    company = await CompanyDAO.get_company(company_name)
    if company is None:
        await state.update_data(name=company_name)
        await state.set_state(CreateCompany.technical_map)
        await message.answer("Спасибо,\nтепер введите техническую карту компании в виде файла")
    else:
        await message.answer("Пожалуй,\nc таким именем компания имеется.\nВведите заново")


@router.message(F.document, or_f(IsAdmin(), IsSuperAdmin()), StateFilter(CreateCompany.technical_map))
async def create_technical_map(message: Message, state: FSMContext):
    f = message.document.file_id
    await state.update_data(technical_map=f)
    new_company = await state.get_data()
    await CompanyDAO.create_company(**new_company)
    await state.set_state(default_state)
    await message.answer("Спасибо, чтобы возврашаться нажмите на /company")
    
 
 
# ========================== Хендлер для список компаний ===============================#
 
 
@router.callback_query(F.data == 'company:list', or_f(IsAdmin(), IsSuperAdmin()), StateFilter(default_state))
async def company_list(cb: CallbackQuery, state: FSMContext):
    companies = await CompanyDAO.list_company()
    keyboard = get_companies_list_kb(companies)
    await cb.message.answer("<b>Список компаний:</b>", reply_markup=keyboard)
    await cb.message.delete()
     

