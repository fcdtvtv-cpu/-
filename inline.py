from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.services.products import get_all_products
from bot.config import settings


def catalog_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for product in get_all_products():
        builder.row(
            InlineKeyboardButton(
                text=f"{product['title']}  ·  {product['price']}",
                callback_data=f"product:{product['id']}",
            )
        )
    return builder.as_markup()


def product_actions_kb(product_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📝 Оставить заявку",
            callback_data=f"order:{product_id}",
        )
    )
    builder.row(
        InlineKeyboardButton(text="« Назад в каталог", callback_data="catalog:back")
    )
    return builder.as_markup()


def safe_deal_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🌐 Перейти на Playerok",
            url=settings.playerok_url,
        )
    )
    builder.row(
        InlineKeyboardButton(text="« В меню", callback_data="menu:back")
    )
    return builder.as_markup()


def admin_order_kb(order_id: int) -> InlineKeyboardMarkup:
    """Кнопка для продавца: клиент оплатил"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Клиент оплатил товар",
            callback_data=f"paid:{order_id}",
        )
    )
    return builder.as_markup()


def rating_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # 0–5 звёзд в один ряд
    buttons = [
        InlineKeyboardButton(text=str(i), callback_data=f"rate:{i}")
        for i in range(6)
    ]
    builder.row(*buttons)
    return builder.as_markup()


def skip_review_text_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Пропустить", callback_data="review:skip_text")
    )
    return builder.as_markup()