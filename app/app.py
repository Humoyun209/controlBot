import logging
from aiogram import Bot, Dispatcher
import asyncio
from handlers.admin_handlers import router as admin_router
from handlers.super_admin_handlers import router as staff_router
from handlers.user_handlers.begin_shift import router as user_begin_router
from handlers.user_handlers.end_shift import router as user_end_router

from config import settings_bot


async def main():
    bot = Bot(token=settings_bot.token, parse_mode='HTML')
    dp = Dispatcher()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - [%(asctime)s] - %(name)s - %(message)s'
    )
    
    dp.include_router(staff_router)
    dp.include_router(admin_router)
    dp.include_router(user_begin_router)
    dp.include_router(user_end_router)
    
    await bot.delete_webhook(True)
    await dp.start_polling(bot)
    

if __name__ == '__main__':
    asyncio.run(main())