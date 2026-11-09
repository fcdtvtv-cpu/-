from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .config import PLAYEROK_URL
from .products import PRODUCTS


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="🔒 Безопасная сделка", callback_data="safe")],
        [InlineKeyboardButton(text="⭐ Завершённые сделки и отзывы", callback_data="revs:0")],
    ])


def catalog_kb() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"{p['title']} — {p['price']}", callback_data=f"prod:{p['id']}")]
        for p in PRODUCTS
    ]
    rows.append([InlineKeyboardButton(text="⬅️ В меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def product_kb(product_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Оформить заявку", callback_data=f"order:{product_id}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="catalog")],
    ])


def cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="menu")],
    ])


def safe_deal_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Перейти на Playerok", url=PLAYEROK_URL)],
        [InlineKeyboardButton(text="⬅️ Выйти в меню", callback_data="menu")],
    ])


def admin_order_kb(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Клиент оплатил товар", callback_data=f"paid:{order_id}")],
    ])


def rating_kb(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=str(i), callback_data=f"rate:{order_id}:{i}") for i in range(0, 6)],
    ])


def skip_comment_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Пропустить", callback_data="skip_comment")],
    ])


def reviews_kb(page: int, total_pages: int) -> InlineKeyboardMarkup:
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"revs:{page - 1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"revs:{page + 1}"))
    rows = [nav] if nav else []
    rows.append([InlineKeyboardButton(text="⬅️ В меню", callback_data="menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
