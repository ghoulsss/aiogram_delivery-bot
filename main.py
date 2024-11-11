import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers.handlers import router
from handlers.callback import router1
from handlers.callback import get_users


async def main():
    load_dotenv()
    token = os.getenv("token")

    bot: Bot = Bot(token=token)
    dp: Dispatcher = Dispatcher()

    dp.include_router(router)
    dp.include_router(router1)
    await get_users()
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
    except Exception as e:
        print("Что-то пошло не так я не работаю, причина:", e)
