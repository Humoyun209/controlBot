from aiogram.fsm.state import StatesGroup, State


class NoneRegisterState(StatesGroup):
    phone = State()