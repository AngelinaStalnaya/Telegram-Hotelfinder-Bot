from aiogram import types

from tgbot_api.keyboards.keyboards import *


async def help_command(message: types.Message):
    text = 'List of commands: \n' \
           ' \t /start - Start the dialog, \n' \
           ' \t /help - Receive the guide on bot`s features, \n' \
           ' \t /lowprice - Best cheap hotels,\n ' \
           ' \t /highprice - Best hotels lux hotels, \n ' \
           ' \t /bestdeal - Best hotels for specified price right in the heart \n ' \
           ' \t\t\t of the location'
    await message.answer(text)


async def start_command(message: types.Message):
    await message.answer(f"Welcome, {message.from_user.full_name}!\n"
                         f"I can help you to find the best place to stay in for your next vacation trip.\n"
                         f"Choose the command to start with!", reply_markup=get_kb_start())


async def other_messages(message: types.Message):
    await message.reply('It`s an ordinary message. Please, select a command to start with.', reply_markup=get_kb_start())


def register_basic_commands(dp) -> None:
    dp.register_message_handler(help_command, commands=['help'], content_types=types.ContentType.TEXT)
    dp.register_message_handler(start_command, commands=['start'], content_types=types.ContentType.TEXT)
    dp.register_message_handler(other_messages, content_types=types.ContentType.TEXT)



