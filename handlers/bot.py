import asyncio
from aiogram import Bot, Dispatcher
from handlers.main_handlers import router


bot = Bot("7929462181:AAEBLXiy-zFomhMieQGJwWLt6gMVlRfUnoM")
dp = Dispatcher()
async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")