"""Точка входа."""
import asyncio
import logging
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
import handlers_user
import handlers_admin
import database as db

logging.basicConfig(level=logging.INFO)


async def main():
    await db.init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.include_router(handlers_admin.router)
    dp.include_router(handlers_user.router)
    
    print(f"✅ Бот запущен")
    
    try:
        await dp.start_polling(bot, allowed_updates=[])
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
