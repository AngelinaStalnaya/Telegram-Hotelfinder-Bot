from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

from tgbot_api.States import PriceStatesGroup
from tgbot_api.keyboards.keyboards import cancel_button
from database.core import crud, RecordHistory


async def lowprice_command(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['sort'] = "PRICE_LOW_TO_HIGH"
        data['command'] = 'lowprice'
        data['user_id'] = message.from_user.id
    await message.answer("<b>Here's going to be <i>the cheapest hotels</i> in location</b>",
                         reply_markup=ReplyKeyboardRemove())
    await PriceStatesGroup.location.set()
    await message.answer('Enter the destination: city/district/place or else..',
                         reply_markup=cancel_button())


async def highprice_command(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['sort'] = "PRICE_HIGH_TO_LOW"
        data['command'] = 'highprice'
        data['user_id'] = message.from_user.id
    await message.answer("<b>Here's going to be <i>lux hotels</i> in location</b>",
                         reply_markup=ReplyKeyboardRemove())
    await PriceStatesGroup.location.set()
    await message.answer('Enter the destination: city/district/place or else.',
                         reply_markup=cancel_button())


async def bestdeal_command(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['sort'] = "bestdeal"
        data['command'] = 'bestdeal'
        data['user_id'] = message.from_user.id
    await message.answer("<b>Here's going to be <i>the best choice hotels </i>in location for sweet price</b>",
                         reply_markup=ReplyKeyboardRemove())
    await PriceStatesGroup.location.set()
    await message.answer('Enter the destination: city/district/place or else.',
                         reply_markup=cancel_button())


async def history_command(message: types.Message):
    history, count = crud.retrieve_history(model=RecordHistory, user_id=message.from_user.id)
    if history:
        for i_request in range(count if count < 10 else 10):
            hotels_message = history[i_request].list_of_hotels.replace("'", '')[1:-1].replace(",", "\n  *")
            await message.answer(f'At: <u>{history[i_request].creation_date}</u>\n'
                                                    f'Command: <b>{history[i_request].operation}</b> \n'
                                                    f'Location:  <b><i>{history[i_request].location}</i></b>\n'
                                                    f'Hotels received: \n  *{hotels_message}.')
        # crud.delete_old(model=RecordHistory, user_id=message.from_user.id)
    else:
        await message.answer_sticker(sticker='CAACAgIAAxkBAAEH9G9j_3Er3x3MTcUd2h4JXf1RC39sYwAC3gUAAj-VzApvED_5xd0MFy4E')
        await message.answer('Your history`s empty yet.')


def register_custom_commands(dp) -> None:
    dp.register_message_handler(lowprice_command, commands=['lowprice'], state=None)
    dp.register_message_handler(highprice_command, commands=['highprice'], state=None)
    dp.register_message_handler(bestdeal_command, commands=['bestdeal'], state=None)
    dp.register_message_handler(history_command, commands=['history'])

