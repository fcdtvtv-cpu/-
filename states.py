from aiogram.fsm.state import State, StatesGroup


class OrderForm(StatesGroup):
    """Форма заявки после выбора услуги"""
    name = State()
    contact = State()
    task = State()


class ReviewForm(StatesGroup):
    """Оценка после оплаты"""
    rating = State()
    text = State()