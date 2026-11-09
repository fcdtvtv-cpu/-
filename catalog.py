import html

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .. import db
from ..config import ADMIN_ID
from ..keyboards import admin_order_kb, cancel_kb, catalog_kb, main_menu, product_kb
from ..products import get_product
from ..states import OrderForm

router = Router()


@router.callback_query(F.data == "catalog")
async def show_catalog(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("🛒 Каталог. Выберите услугу:", reply_markup=catalog_kb())
    await call.answer()


@router.callback_query(F.data.startswith("prod:"))
async def show_product(call: CallbackQuery):
    product = get_product(call.data.split(":", 1)[1])
    if not product:
        await call.answer("Товар не найден", show_alert=True)
        return
    await call.message.edit_text(
        f"<b>{html.escape(product['title'])}</b>\n"
        f"Цена: {html.escape(product['price'])}\n\n"
        f"{html.escape(product['description'])}",
        reply_markup=product_kb(product["id"]),
        parse_mode="HTML",
    )
    await call.answer()


@router.callback_query(F.data.startswith("order:"))
async def start_order(call: CallbackQuery, state: FSMContext):
    product = get_product(call.data.split(":", 1)[1])
    if not product:
        await call.answer("Товар не найден", show_alert=True)
        return
    await state.clear()
    await state.update_data(product_id=product["id"])
    await state.set_state(OrderForm.name)
    await call.message.edit_text("Как вас зовут? Напишите имя:", reply_markup=cancel_kb())
    await call.answer()


@router.message(OrderForm.name, F.text)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(OrderForm.contact)
    await message.answer(
        "Оставьте контакт для связи (Telegram @username, телефон и т.п.):",
        reply_markup=cancel_kb(),
    )


@router.message(OrderForm.contact, F.text)
async def get_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text.strip())
    await state.set_state(OrderForm.task)
    await message.answer("Опишите вашу задачу:", reply_markup=cancel_kb())


@router.message(OrderForm.task, F.text)
async def get_task(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()

    product = get_product(data["product_id"])
    if not product:
        await message.answer("Товар больше недоступен.", reply_markup=main_menu())
        return

    user = message.from_user
    order_id = await db.create_order(
        user_id=user.id,
        username=user.username,
        product_id=product["id"],
        product_title=product["title"],
        name=data["name"],
        contact=data["contact"],
        task=message.text.strip(),
    )

    uname = f"@{user.username}" if user.username else "нет username"
    await bot.send_message(
        ADMIN_ID,
        f"📩 <b>Новая заявка #{order_id}</b>\n\n"
        f"Товар: {html.escape(product['title'])} — {html.escape(product['price'])}\n"
        f"Имя: {html.escape(data['name'])}\n"
        f"Контакт: {html.escape(data['contact'])}\n"
        f"Telegram: {html.escape(uname)} (id {user.id})\n\n"
        f"Задача:\n{html.escape(message.text.strip())}",
        reply_markup=admin_order_kb(order_id),
        parse_mode="HTML",
    )

    await message.answer(
        "✅ Ваша заявка отправлена, ожидайте ответа.\n\n"
        "Продавец может быть занят. Оплата товара — после того, "
        "как продавец напишет вам.",
        reply_markup=main_menu(),
    )
