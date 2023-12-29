from aiogram.fsm.state import StatesGroup, State


class InShift(StatesGroup):
    in_shift: State = State()
    

class BeginShiftState(StatesGroup):
    grams_of_tobacco = State()
    summa = State()
    photo_group = State()
    

class EndShiftState(StatesGroup):
    grams_of_tobacco = State()
    summa = State()
    photo_group = State()
    quantity_of_sold = State()
    promo_quantity = State()
    card = State()
    cash = State()
    in_club = State()
    in_club_card = State()
    in_club_cash = State()
    tips = State()
