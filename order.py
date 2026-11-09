from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.config import settings
from bot.states import OrderForm, ReviewForm
from bot.keyboards.reply import main_menu, cancel_kb
from bot.keyboards.inline import (
    product_actions_kb,
    admin_order_kb,
    rating_kb,
    skip_review_text_kb,
    catalog_kb,
)
from bot.services.products import get_product
from bot.services.storage import (
    save_order,
    get_order,
    update_order_status,
    save_review,
    get_last_paid_order,
)

router = Router(name="order")


# ---------- Просмотр услуги ----------

@router.callback_query(F.data.startswith("product:"))
async def show_product(callback: CallbackQuery) -> None:
    product_id = callback.data.split(":")[1]
    product = get_product(product_id)
    if not product:
        await callback.answer("Услуга не найдена", show_alert=True)
        return

    text = (
        f"<b>{product['title']}</b>\n\n"
        f"{product['description']}\n\n"
        f"💰 Цена: <b>{product['price']}</b>"
    )
    await callback.message.edit_text(
        text,
        reply_markup=product_actions_kb(product_id),
    )
    await callback.answer()


# ---------- Старт формы заявки ----------

@router.callback_query(F.data.startswith("order:"))
async def start_order(callback: CallbackQuery, state: FSMContext) -> None:
    product_id = callback.data.split(":")[1]
    product = get_product(product_id)
    if not product:
        await callback.answer("Услуга не найдена", show_alert=True)
        return

    await state.clear()
    await state.update_data(
        product_id=product_id,
        product_title=product["title"],
    )
    await state.set_state(OrderForm.name)

    await callback.message.edit_text(
        f"Вы выбрали: <b>{product['title']}</b>\n\n"
        "<b>Шаг 1/3</b>\n"
        "Как вас зовут?"
    )
    await callback.message.answer(
        "Введите имя или нажмите «Отмена»:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.message(OrderForm.name, F.text == "❌ Отмена")
@router.message(OrderForm.contact, F.text == "❌ Отмена")
@router.message(OrderForm.task, F.text == "❌ Отмена")
async def cancel_order(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "Заявка отменена.",
        reply_markup=main_menu(),
    )


@router.message(OrderForm.name)
async def process_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if len(name) < 2:
        await message.answer("Введите корректное имя (минимум 2 символа).")
        return
    await state.update_data(name=name)
    await state.set_state(OrderForm.contact)
    await message.answer(
        f"Приятно познакомиться, <b>{name}</b>!\n\n"
        "<b>Шаг 2/3</b>\n"
        "Укажите удобный способ связи:\n"
        "• Telegram (@username)\n"
        "• Телефон\n"
        "• Email",
        reply_markup=cancel_kb(),
    )


@router.message(OrderForm.contact)
async def process_contact(message: Message, state: FSMContext) -> None:
    contact = (message.text or "").strip()
    if len(contact) < 3:
        await message.answer("Укажите корректный контакт.")
        return
    await state.update_data(contact=contact)
    await state.set_state(OrderForm.task)
    await message.answer(
        "<b>Шаг 3/3</b>\n"
        "Опишите задачу / что именно нужно:",
        reply_markup=cancel_kb(),
    )


@router.message(OrderForm.task)
async def process_task(message: Message, state: FSMContext, bot: Bot) -> None:
    task = (message.text or "").strip()
    if len(task) < 3:
        await message.answer("Пожалуйста, опишите задачу чуть подробнее.")
        return

    data = await state.get_data()
    await state.clear()

    order = save_order({
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "full_name": message.from_user.full_name,
        "name": data["name"],
        "contact": data["contact"],
        "task": task,
        "product_id": data["product_id"],
        "product_title": data["product_title"],
    })

    # Сообщение клиенту
    await message.answer(
        "✅ <b>Ваша заявка отправлена!</b>\n\n"
        "Ожидайте ответа. Продавец может быть занят.\n"
        "Оплата товара — <b>после того, как продавец напишет вам</b>.",
        reply_markup=main_menu(),
    )

    # Уведомление продавцу
    username = f"@{message.from_user.username}" if message.from_user.username else "нет"
    admin_text = (
        f"<b>📋 Новая заявка #{order['id']}</b>\n"
        f"{'─' * 24}\n"
        f"<b>Услуга:</b> {data['product_title']}\n"
        f"<b>Имя:</b> {data['name']}\n"
        f"<b>Контакт:</b> {data['contact']}\n"
        f"<b>Задача:</b>\n{task}\n"
        f"{'─' * 24}\n"
        f"<b>От:</b> {message.from_user.full_name} ({username})\n"
        f"<b>ID:</b> <code>{message.from_user.id}</code>"
    )

    try:
        await bot.send_message(
            chat_id=settings.admin_id,
            text=admin_text,
            reply_markup=admin_order_kb(order["id"]),
        )
    except Exception:
        pass


# ---------- Продавец нажал «Клиент оплатил» ----------

@router.callback_query(F.data.startswith("paid:"))
async def mark_paid(callback: CallbackQuery, bot: Bot, state: FSMContext) -> None:
    if callback.from_user.id != settings.admin_id:
        await callback.answer("Только для продавца", show_alert=True)
        return

    order_id = int(callback.data.split(":")[1])
    order = get_order(order_id)
    if not order:
        await callback.answer("Заявка не найдена", show_alert=True)
        return

    if order.get("status") == "paid":
        await callback.answer("Уже отмечено как оплаченное", show_alert=True)
        return

    update_order_status(order_id, "paid")

    # Обновляем сообщение продавца
    original = callback.message.html_text or callback.message.text or ""
    await callback.message.edit_text(
        original + "\n\n✅ <b>Клиент оплатил</b>",
        reply_markup=None,
    )
    await callback.answer("Статус обновлён")

    # Просим клиента оценить
    try:
        await bot.send_message(
            chat_id=order["user_id"],
            text=(
                "🎉 Сделка завершена!\n\n"
                "<b>Оставьте отзыв, как прошла сделка?</b>\n"
                "Оцените от 0 до 5:"
            ),
            reply_markup=rating_kb(),
        )
        # Сохраняем order_id в state пользователя через data (проще через callback)
    except Exception:
        pass


# ---------- Оценка ----------

@router.callback_query(F.data.startswith("rate:"))
async def process_rating(callback: CallbackQuery, state: FSMContext) -> None:
    rating = int(callback.data.split(":")[1])
    if rating < 0 or rating > 5:
        await callback.answer("Некорректная оценка")
        return

    await state.update_data(rating=rating)
    await state.set_state(ReviewForm.text)

    await callback.message.edit_text(
        f"Вы поставили: <b>{rating}/5</b>\n\n"
        "Напишите короткий комментарий (или нажмите «Пропустить»):",
        reply_markup=skip_review_text_kb(),
    )
    await callback.answer()


@router.callback_query(ReviewForm.text, F.data == "review:skip_text")
async def skip_review_text(callback: CallbackQuery, state: FSMContext) -> None:
    await _finish_review(callback, state, text=None)
    await callback.answer()


@router.message(ReviewForm.text)
async def process_review_text(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    await _finish_review_message(message, state, text=text)


async def _finish_review(callback: CallbackQuery, state: FSMContext, text: str | None) -> None:
    data = await state.get_data()
    rating = data.get("rating", 0)
    await state.clear()

    order = get_last_paid_order(callback.from_user.id) or {}

    save_review({
        "user_id": callback.from_user.id,
        "name": order.get("name") or callback.from_user.full_name,
        "rating": rating,
        "text": text,
        "product_title": order.get("product_title"),
        "order_id": order.get("id"),
    })

    if order.get("id"):
        update_order_status(order["id"], "reviewed")

    await callback.message.edit_text(
        "Спасибо за отзыв! 🙏\n"
        "Он появится в разделе «⭐ Отзывы»."
    )
    await callback.message.answer("Главное меню:", reply_markup=main_menu())


async def _finish_review_message(message: Message, state: FSMContext, text: str | None) -> None:
    data = await state.get_data()
    rating = data.get("rating", 0)
    await state.clear()

    order = get_last_paid_order(message.from_user.id) or {}

    save_review({
        "user_id": message.from_user.id,
        "name": order.get("name") or message.from_user.full_name,
        "rating": rating,
        "text": text,
        "product_title": order.get("product_title"),
        "order_id": order.get("id"),
    })

    if order.get("id"):
        update_order_status(order["id"], "reviewed")

    await message.answer(
        "Спасибо за отзыв! 🙏\n"
        "Он появится в разделе «⭐ Отзывы».",
        reply_markup=main_menu(),
    )