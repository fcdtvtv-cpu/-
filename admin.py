from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery

from .. import db
from ..config import ADMIN_ID
from ..keyboards import rating_kb

router = Router()


@router.callback_query(F.data.startswith("paid:"))
async def client_paid(call: CallbackQuery, bot: Bot):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Только для продавца", show_alert=True)
        return

    order_id = int(call.data.split(":", 1)[1])
    order = await db.get_order(order_id)
    if not order:
        await call.answer("Заявка не найдена", show_alert=True)
        return

    if not await db.mark_paid(order_id):
        await call.answer("Уже отмечено как оплаченное", show_alert=True)
        return

    await call.message.edit_text(
        call.message.html_text + "\n\n💰 <b>Оплачено. Запрос отзыва отправлен клиенту.</b>",
        parse_mode="HTML",
        reply_markup=None,
    )

    await bot.send_message(
        order["user_id"],
        "Оставьте отзыв: как прошла сделка?\n"
        "Оцените площадку продаж и продавца от 0 до 5:",
        reply_markup=rating_kb(order_id),
    )
    await call.answer("Готово")
