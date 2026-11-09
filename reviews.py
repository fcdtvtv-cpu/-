import html
import math

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from .. import db
from ..config import ADMIN_ID, REVIEWS_PER_PAGE
from ..keyboards import main_menu, reviews_kb, skip_comment_kb
from ..states import ReviewForm

router = Router()


@router.callback_query(F.data.startswith("rate:"))
async def rate(call: CallbackQuery, state: FSMContext):
    _, order_id, rating = call.data.split(":")
    order_id, rating = int(order_id), int(rating)

    if not await db.set_rating(order_id, call.from_user.id, rating):
        await call.answer("Оценка уже сохранена", show_alert=True)
        return

    await state.set_state(ReviewForm.comment)
    await state.update_data(order_id=order_id)
    await call.message.edit_text(
        f"Спасибо! Ваша оценка: {rating}/5.\n\n"
        "Напишите сообщение к отзыву или нажмите «Пропустить».",
        reply_markup=skip_comment_kb(),
    )
    await call.answer()


async def _finish(order_id: int, bot: Bot):
    order = await db.get_order(order_id)
    comment = order["comment"] or "—"
    await bot.send_message(
        ADMIN_ID,
        f"⭐ Новый отзыв по заявке #{order_id}: {order['rating']}/5\n"
        f"{html.escape(comment)}",
        parse_mode="HTML",
    )


@router.message(ReviewForm.comment, F.text)
async def get_comment(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()
    await db.set_comment(data["order_id"], message.from_user.id, message.text.strip())
    await message.answer(
        "Спасибо за отзыв! Он появится в разделе «Завершённые сделки и отзывы».",
        reply_markup=main_menu(),
    )
    await _finish(data["order_id"], bot)


@router.callback_query(F.data == "skip_comment", ReviewForm.comment)
async def skip_comment(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()
    await call.message.edit_text("Спасибо за оценку!", reply_markup=main_menu())
    await call.answer()
    await _finish(data["order_id"], bot)


def _mask(name: str) -> str:
    return name[0] + "***" if name else "Аноним"


@router.callback_query(F.data.startswith("revs:"))
async def show_reviews(call: CallbackQuery):
    page = int(call.data.split(":", 1)[1])
    total = await db.count_reviews()
    if total == 0:
        await call.message.edit_text(
            "Пока нет завершённых сделок.", reply_markup=reviews_kb(0, 1)
        )
        await call.answer()
        return

    total_pages = math.ceil(total / REVIEWS_PER_PAGE)
    page = max(0, min(page, total_pages - 1))
    rows = await db.list_reviews(page * REVIEWS_PER_PAGE, REVIEWS_PER_PAGE)
    avg = await db.average_rating()

    lines = [f"⭐ Завершённые сделки: {total} | Средняя оценка: {avg:.1f}/5\n"]
    for r in rows:
        lines.append(
            f"<b>{_mask(r['name'])}</b> — {html.escape(r['product_title'])}\n"
            f"Оценка: {r['rating']}/5\n"
            f"{html.escape(r['comment']) if r['comment'] else ''}\n"
        )
    lines.append(f"Стр. {page + 1}/{total_pages}")

    await call.message.edit_text(
        "\n".join(lines), reply_markup=reviews_kb(page, total_pages), parse_mode="HTML"
    )
    await call.answer()
