from aiogram.fsm.state import StatesGroup, State


class CreateCompany(StatesGroup):
    name = State()
    technical_map = State()
