from aiogram import Bot, Dispatcher
import asyncio
import logging
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from dotenv import load_dotenv
from config import TOKEN, RAILWAY_PUBLIC_URL, WEBHOOK_PATH, PORT, WEBHOOK_URL
from aiohttp import web
from captcha import start_router
from choose_category import category_router

load_dotenv()

# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Регистрация роутеров
dp.include_router(start_router)
dp.include_router(category_router)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def on_startup():
    """Действия при запуске приложения"""
    if WEBHOOK_URL:
        await bot.set_webhook(WEBHOOK_URL)
        logger.info(f"✅ Webhook установлен: {WEBHOOK_URL}")
    
    me = await bot.get_me()
    logger.info(f"🤖 Бот @{me.username} запущен!")

async def on_shutdown():
    """Действия при остановке приложения"""
    await bot.session.close()
    logger.info("❌ Бот остановлен")

async def health_check(request):
    """Health check для Railway"""
    return web.Response(text="✅ Бот работает!")

async def root_handler(request):
    """Корневой маршрут"""
    return web.Response(text="🚀 Telegram Bot is running on Railway!")

def main():
    # Создаем aiohttp приложение
    app = web.Application()
    
    # Добавляем маршруты
    app.router.add_get("/", root_handler)
    app.router.add_get("/health", health_check)
    
    # Настраиваем webhook обработчик
    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_handler.register(app, path=WEBHOOK_PATH)
    
    # Настройка приложения
    setup_application(app, dp, bot=bot)
    
    # Запускаем приложение
    logger.info(f"🌐 Сервер запускается на порту {PORT}")
    web.run_app(
        app,
        host='0.0.0.0',  # Важно для Railway!
        port=PORT
    )

if __name__ == "__main__":
    # Выполняем startup действия
    import asyncio
    asyncio.run(on_startup())
    
    # Запускаем основное приложение
    main()