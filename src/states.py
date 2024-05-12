from aiogram.fsm.state import StatesGroup, State


class States(StatesGroup):
    SELECTING_CATEGORY = State()
    ENTERING_NAME = State()
    ENTERING_LINK = State()
    ENTERING_REASON = State()