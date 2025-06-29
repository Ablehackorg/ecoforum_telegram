import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router, bot
from database.db import init_db
from utils.scheduler import setup_scheduler

logging.basicConfig(level=logging.INFO)
    
async def main():
    init_db()
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    setup_scheduler(bot)

    logging.info("🤖 Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())