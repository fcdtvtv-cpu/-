from aiogram.fsm.state import State, StatesGroup


class OrderForm(StatesGroup):
    name = State()
    contact = State()
    task = State()


class ReviewForm(StatesGroup):
    comment = State()
