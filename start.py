from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from ..keyboards import main_menu, safe_deal_kb

router = Router()

WELCOME = "👋 Добро пожаловать в Exe shop!\n\nВыберите раздел:"


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(WELCOME, reply_markup=main_menu())


@router.callback_query(F.data == "menu")
async def to_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(WELCOME, reply_markup=main_menu())
    await call.answer()


@router.callback_query(F.data == "safe")
async def safe_deal(call: CallbackQuery):
    await call.message.edit_text(
        "🔒 Безопасная сделка\n\n"
        "Вот профиль и товары на Playerok для безопасной сделки.\n"
        "Вы можете перейти на сайт или выйти в меню.",
        reply_markup=safe_deal_kb(),
    )
    await call.answer()
