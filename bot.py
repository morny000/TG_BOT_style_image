import asyncio
from aiogram import Bot, Dispatcher
from handlers.main_handlers import router


bot = Bot("7957890010:AAGeS6R8fmNdBkjwDgQSR5IExSAdt-WXRrw")
dp = Dispatcher()
async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")