from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.config import settings
from bot.keyboards.reply import main_menu
from bot.keyboards.inline import catalog_kb, safe_deal_kb
from bot.services.storage import get_all_reviews, get_reviews_stats

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    text = (
        f"👋 Добро пожаловать в <b>{settings.shop_name}</b>!\n\n"
        "Здесь вы можете выбрать услугу, оставить заявку "
        "и оформить безопасную сделку.\n\n"
        "Выберите раздел в меню ниже 👇"
    )
    await message.answer(text, reply_markup=main_menu())


@router.message(F.text == "🛒 Каталог")
async def show_catalog(message: Message) -> None:
    await message.answer(
        "<b>🛒 Каталог услуг</b>\n\n"
        "Выберите интересующую услугу:",
        reply_markup=catalog_kb(),
    )


@router.callback_query(F.data == "catalog:back")
async def catalog_back(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "<b>🛒 Каталог услуг</b>\n\n"
        "Выберите интересующую услугу:",
        reply_markup=catalog_kb(),
    )
    await callback.answer()


@router.message(F.text == "🔒 Безопасная сделка")
async def safe_deal(message: Message) -> None:
    text = (
        "<b>🔒 Безопасная сделка</b>\n\n"
        "Для максимальной защиты рекомендуем оформлять "
        "покупку через площадку <b>Playerok</b>.\n\n"
        "Там есть гарантии, отзывы и безопасная оплата.\n\n"
        f"Профиль с товарами:\n"
        f"<code>{settings.playerok_url}</code>"
    )
    await message.answer(text, reply_markup=safe_deal_kb())


@router.callback_query(F.data == "menu:back")
async def menu_back(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.message.answer(
        "Главное меню:",
        reply_markup=main_menu(),
    )
    await callback.answer()


@router.message(F.text == "⭐ Отзывы")
async def show_reviews(message: Message) -> None:
    stats = get_reviews_stats()
    reviews = get_all_reviews()

    if not reviews:
        await message.answer(
            "<b>⭐ Отзывы</b>\n\n"
            "Пока нет завершённых сделок с отзывами.\n"
            "Будьте первым!",
            reply_markup=main_menu(),
        )
        return

    stars = "⭐" * int(round(stats["avg"])) if stats["avg"] else "—"
    header = (
        f"<b>⭐ Отзывы покупателей</b>\n"
        f"Средняя оценка: <b>{stats['avg']}</b> {stars} "
        f"({stats['count']} шт.)\n"
        f"{'─' * 24}\n"
    )

    # Показываем последние 10 отзывов
    lines = []
    for r in reversed(reviews[-10:]):
        rating = r.get("rating", 0)
        text = r.get("text") or "без комментария"
        name = r.get("name") or "Покупатель"
        product = r.get("product_title") or "услуга"
        lines.append(
            f"{'⭐' * rating}{'☆' * (5 - rating)}  <b>{name}</b>\n"
            f"<i>{product}</i>\n"
            f"{text}"
        )

    body = "\n\n".join(lines)
    await message.answer(header + body, reply_markup=main_menu())


@router.message(F.text == "ℹ️ О магазине")
async def about_shop(message: Message) -> None:
    text = (
        f"<b>ℹ️ О магазине {settings.shop_name}</b>\n\n"
        "Мы продаём качественные услуги и товары.\n\n"
        "• Быстрая связь после заявки\n"
        "• Возможность безопасной сделки через Playerok\n"
        "• Реальные отзывы покупателей\n\n"
        "Выберите услугу в каталоге и оставьте заявку — "
        "я свяжусь с вами лично."
    )
    await message.answer(text, reply_markup=main_menu())


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "<b>Помощь</b>\n\n"
        "🛒 <b>Каталог</b> — выбрать услугу и оставить заявку\n"
        "🔒 <b>Безопасная сделка</b> — перейти на Playerok\n"
        "⭐ <b>Отзывы</b> — посмотреть оценки покупателей\n\n"
        "После заявки продавец свяжется с вами в личных сообщениях.",
        reply_markup=main_menu(),
    )