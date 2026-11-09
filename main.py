import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot import db
from bot.config import BOT_TOKEN
from bot.handlers import all_routers


async def main():
    logging.basicConfig(level=logging.INFO)
    if not BOT_TOKEN:
        raise SystemExit("Не задан BOT_TOKEN в .env")

    await db.init_db()
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    for r in all_routers():
        dp.include_router(r)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
