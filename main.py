import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from settings import start_bot
from tgbot_api.handlers.handlers_core import register_all_handlers


# Configure logging
logging.basicConfig(level=logging.INFO)


# Initialize bot, dispatcher, memory storage

API_TOKEN = start_bot.bot_token.get_secret_value()
storage = MemoryStorage()
bot = Bot(token=API_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot=bot, storage=storage)


async def on_startup(_):
    print("I've been started up!")
    register_all_handlers(dp)


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, on_startup=on_startup,
                                          skip_updates=True)
