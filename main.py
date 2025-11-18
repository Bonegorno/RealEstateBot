from aiogram import Bot, Dispatcher
import asyncio
import logging
from dotenv import load_dotenv
from config import TOKEN
from captcha import start_router
from choose_category import category_router

load_dotenv()

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(start_router)
dp.include_router(category_router)
logging.basicConfig(level=logging.INFO)
    
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())