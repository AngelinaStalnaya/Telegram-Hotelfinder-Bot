from loguru import logger

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from settings import start_bot
from tgbot_api.handlers.handlers_core import register_all_handlers


# Configure logger
logger.remove(0)
logger.add('logging_file.log', format='{time: DD.MM.YYYY at HH: mm: ss} -  {level} - {message}',
                     level='DEBUG', rotation='5 MB', compression='zip')

# Initialize bot, dispatcher, memory storage

API_TOKEN = start_bot.bot_token.get_secret_value()
storage = MemoryStorage()
bot = Bot(token=API_TOKEN, parse_mode='HTML')
dp = Dispatcher(bot=bot, storage=storage)


async def on_startup(_) -> None:  # function called while starting the bot
    logger.info('The bot has been started up!')
    register_all_handlers(dp)


async def on_shutdown(_) -> None:  # function called while stopping the bot
    logger.info('The bot has been stopped.')


@logger.catch
def main():  # main function to start the bot
    executor.start_polling(dispatcher=dp, on_startup=on_startup,
                           skip_updates=True, on_shutdown=on_shutdown)


if __name__ == '__main__':   # entry point
     main()
