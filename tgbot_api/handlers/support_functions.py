import asyncio
from datetime import datetime


from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove, ForceReply
from aiogram.utils.callback_data import CallbackData
from aiogram_calendar import SimpleCalendar, simple_cal_callback

from database.core import PriceSort, BestPrice, Photo, AnswerMaker, \
                                               RecordHistory, Hotels, crud
from site_api.site_api_core import site_api
from tgbot_api.States import *
from tgbot_api.keyboards.keyboards import *


async def cb_cancel(message: types.Message, state: FSMContext) -> None:  # function for cancel of the command
    await state.finish()
    await message.answer('You`ve terminated the action of the command.',
                                            reply_markup=get_kb_start())


async def create_history(state: FSMContext) -> None:   # function for recording user`s history
    async with state.proxy() as data:
        user_id = data['user_id']
    hotels, all_amount_hotels = crud.retrieve_hotels_for_db(model=AnswerMaker, user_id=user_id)
    hotels_in_answer = [hotels[i_part].hotel_name for i_part in range(all_amount_hotels)]
    load = [hotels[0].user_id, hotels[0].command, hotels[0].location_name, hotels_in_answer, datetime.now().strftime("%d/%m/%Y %H:%M:%S")]
    crud.create(model=RecordHistory, data=load)
    crud.delete_answers(model=AnswerMaker, user_id=user_id)
    await state.finish()


async def find_location(message: types.Message, state: FSMContext) -> None:  # function for location check
    response = await site_api.get_location(message.text)
    await asyncio.sleep(0.1)
    if response:
        async with state.proxy() as data:
            data['location'] = response
        await message.answer('Please, select check in date: ',
                                                reply_markup=await SimpleCalendar().start_calendar())
        await PriceStatesGroup.check_in.set()
    else:
        await message.answer('Sorry, the bot can`t find the location. \n'
                                                'Please, try again.')


async def check_in_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext) -> None:  # function for check in date check
    selected, date = await SimpleCalendar().process_selection(query=callback_query, data=callback_data)
    if selected:
        await callback_query.message.answer(f'From: {date.strftime("%d/%m/%Y")}',
                                                                          reply_markup=ReplyKeyboardRemove())
        async with state.proxy() as data:
            data['checkInDate'] = date.strftime("%d/%m/%Y")
        await callback_query.message.answer('Please, select check out date: ', reply_markup=await SimpleCalendar().start_calendar())
        await PriceStatesGroup.check_out.set()


async def check_out_calendar(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext) -> None:  # function for check out date check
    selected, date = await SimpleCalendar().process_selection(query=callback_query, data=callback_data)
    if selected:
        await callback_query.message.answer(f'To: {date.strftime("%d/%m/%Y")}',
                                                                          reply_markup=ReplyKeyboardRemove())
        async with state.proxy() as data:
            data['checkOutDate'] = date.strftime("%d/%m/%Y")
            if data['sort'] != 'bestdeal':
                load = [callback_query.message.from_user.id,
                        data['sort'],
                        data['location']['gaiaId'],
                        data['location']['coordinates']['lat'],
                        data['location']['coordinates']['long'],
                        data['location']['fullName'],
                        data['checkInDate'],
                        data['checkOutDate']]
                crud.create(model=PriceSort, data=load)
                uploaded_data = crud.retrieve_all(model=PriceSort)[0]
                data['id_line'] = uploaded_data.id
                result = await site_api.get_all_price(location=uploaded_data.location_gaia,
                                                                   sort=uploaded_data.sort,
                                                                   check_in=uploaded_data.check_in,
                                                                   check_out=uploaded_data.check_out)
                if result:
                    data['site_results'] = result
                    await callback_query.message.answer(f'We`ve found {len(result)} hotels. '
                                                                                      f'Please, limit the result size.',
                                                                                      reply_markup=ForceReply())
                    await PriceStatesGroup.result_size.set()
            else:
                await PriceStatesGroup.cost_max.set()
                await callback_query.message.answer('Enter max price limit for 1 night: ')


async def max_price_limit(message: types.Message, state: FSMContext) -> None:  # function for max price limit input
    if message.text.isdigit():
        async with state.proxy() as data:
            data['cost_max'] = int(message.text)
            await PriceStatesGroup.cost_min.set()
            await message.answer('Enter a min price limit for 1 night: ')
    else:
        await message.reply('It`s not a number. Please, try again.')


async def min_price_limit(message: types.Message, state: FSMContext) -> None:  # function for min price limit input
    if message.text.isdigit():
        async with state.proxy() as data:
            data['cost_min'] = int(message.text)
            await PriceStatesGroup.distance_max.set()
            await message.answer('Enter a max distance from the center of the location: ')
    else:
        await message.reply('It`s not a number. Please, try again.')


async def distance_limit(message: types.Message, state: FSMContext) -> None:  # function for distance input check
    if message.text.isdigit():
        async with state.proxy() as data:
            data['distance_max'] = int(message.text)
            load = [message.from_user.id,
                          data['sort'],
                          data['location']['gaiaId'],
                          data['location']['coordinates']['lat'],
                          data['location']['coordinates']['long'],
                          data['location']['fullName'],
                          data['checkInDate'],
                          data['checkOutDate'],
                          data['cost_max'],
                          data['cost_min'],
                          data['distance_max']]
            crud.create(model=BestPrice, data=load)
            uploaded_data = crud.retrieve_all(model=BestPrice)[0]
            data['id_line'] = uploaded_data.id
            try:
                result = await site_api.get_bestdeal(location_gaia=uploaded_data.location_gaia,
                                                               location_lat=uploaded_data.location_lat,
                                                               location_long=uploaded_data.location_long,
                                                               check_in=uploaded_data.check_in,
                                                               check_out=uploaded_data.check_out,
                                                               cost_max=uploaded_data.cost_max,
                                                               cost_min=uploaded_data.cost_min,
                                                               distance_max=uploaded_data.distance_max)
                if result:
                    data['site_results'] = result
                    await message.answer(f'We`ve found {len(result)} hotels. '
                                         f'Please, limit the result size.',
                                         reply_markup=ForceReply())
                    await PriceStatesGroup.result_size.set()
            except Exception:
                await message.answer_sticker(sticker='CAACAgIAAxkBAAEH9FVj_21SrQVXrPqhaw0btrJ-VCzuCwACvwUAAj-VzAr5wuwdpEkoEy4E')
                await message.answer('We are sorry for not finding hotels for your request. \n'
                                     'Please, start again.', reply_markup=get_kb_start())
                await state.finish()
    else:
        await message.reply('It`s not a number. Please, try again.')


async def result_limit(message: types.Message, state: FSMContext) -> None:  # function for result limit input
    if message.text.isdigit():
        async with state.proxy() as data:
            if int(message.text) > len(data['site_results']):
                amount = len(data['site_results'])
            else:
                amount = int(message.text)
            crud.update(model=PriceSort if data['sort'] != 'bestdeal' else BestPrice,
                                 id_line=data['id_line'], amount=amount, success=0)
            for hotel in data['site_results'][0: amount]:
                load = [message.from_user.id, hotel['property_id'],
                              hotel['price_for_night'], hotel['price_total'],
                              data['location']['gaiaId'], hotel['name'], hotel['distance'],
                              data['command'], data['location']['fullName']]
                crud.create(model=AnswerMaker, data=load)
        await take_next_hotel(user_id=message.from_user.id, message=message, state=state)
    else:
        await message.reply('It`s not a number. Please, try again.')


async def take_next_hotel(user_id: int, message: types.Message, state: FSMContext) -> None:  # function for retrieving hotel`s info from db
    hotel = crud.retrieve_hotel(model=AnswerMaker, user_id=user_id)
    if hotel:
        await check_hotel_in_db(hotel=hotel[0], message=message)
    else:
        await message.answer('Have a nice time!')
        await message.answer_sticker(sticker='CAACAgIAAxkBAAEH8plj_xW5BmdLAYeC5NDs3cbpAAHCJl4AAtMFAAI_lcwKn1q70l1HxzEuBA')
        await create_history(state=state)


async def check_hotel_in_db(hotel, message: types.Message) -> None:  # function for hotel`s info check in db / recording info in db

    check = crud.check_hotel(model=Hotels, hotel_id=hotel.hotel_id)
    if check:
        await send_hotels(message=message, data=check[0], hotel_data=hotel)
    else:
        all_amount_photo, address = await site_api.get_photos_and_address(property_id=hotel.hotel_id)
        hotel_url = await site_api.get_property_url(region_id=hotel.location,
                                                                        property_id=hotel.hotel_id)
        load = [hotel.hotel_id, hotel.hotel_name, address, hotel.distance,
                   hotel_url, all_amount_photo]
        crud.create(model=Hotels, data=load)
        to_send_user = crud.check_hotel(model=Hotels, hotel_id=hotel.hotel_id)[0]
        await send_hotels(message=message, data=to_send_user, hotel_data=hotel)


async def send_hotels(message: types.Message, data, hotel_data) -> None:  # function for sending message with hotel`s info to the user
    await message.answer(f"{data.hotel_name} \n "
                                            f"Situated at: {data.address} \n"
                                            f"which is {data.distance} km from the centre. \n"
                                            f"Price before discounts is {hotel_data.total_cost}. \n"
                                            f"{hotel_data.cost}. \n"
                                            f"For more details visit: {data.url} \n\n "
                                            f"<b>We`ve found {data.all_photo} photos of this hotel.</b> \n "
                                            f"Do you want to see?",
                                            reply_markup=need_photos(hotel_id=data.hotel_id))
    await PhotoState.need_photo.set()


async def load_photo(callback: types.CallbackQuery, state: FSMContext) -> None:  # function for photo necessity  check
    await callback.message.edit_reply_markup()
    async with state.proxy() as data:
        if callback.data.startswith('Yes'):
            data['hotel_id'] = callback.data[5:]
            await callback.message.answer('Please, limit the number of photos.', reply_markup=ForceReply())
            await PhotoState.photo_amount.set()
        else:
            data['hotel_id'] = callback.data[4:]
            crud.update(model=AnswerMaker, hotel_id=data['hotel_id'], amount=0)
            crud.update(model=AnswerMaker, hotel_id=data['hotel_id'], success=1)
            await take_next_hotel(user_id=callback.message.from_user.id, message=callback.message, state=state)


async def photo_limit(message: types.Message, state: FSMContext):  # function for hotel`s photo sending
    if message.text.isdigit():
        async with state.proxy() as data:
            all_amount = crud.check_hotel(model=Hotels, hotel_id=data['hotel_id'])[0].all_photo
            if int(message.text) > all_amount:
                amount = all_amount
            else:
                amount = int(message.text)
            data['amount'] = amount
            await message.delete()
            crud.update(model=AnswerMaker, hotel_id=data['hotel_id'], amount=amount)
            photos = crud.retrieve_photo(model=Photo, hotel_id=data['hotel_id'],
                                                                photo_amount=amount)
            count = 0
            media = types.MediaGroup()
            if len(photos) > 10:
                for i_parts in range(amount // 10):
                    for i_photo in range(10):
                        i_photo += count
                        media.attach_photo(photo=f'{photos[ i_photo].urls}')
                    try:
                        await message.answer_media_group(media=media, disable_notification=True)
                    except Exception :
                        await message.answer('Something`s wrong. The bot can`t send you photos.')
                    count += 10
                    media = types.MediaGroup()
                for i_photo in range(amount % 10):
                    media.attach_photo(photo=f'{photos[count + i_photo].urls}')
                try:
                    await message.answer_media_group(media=media, disable_notification=True)
                except Exception :
                    await message.answer('Something`s wrong. The bot can`t send you photos.')
            else:
                for i_photo in range(amount):
                    media.attach_photo(photo=f'{photos[i_photo].urls}')
                try:
                    await message.answer_media_group(media=media, disable_notification=True)
                except Exception :
                    await message.answer('Something`s wrong. The bot can`t send you photos.')
        crud.update(model=AnswerMaker, hotel_id=data['hotel_id'], success=1)
        await take_next_hotel(user_id=message.from_user.id, message=message, state=state)
    else:
        await message.reply('It`s not a number. Please, try again.')


def register_support_functions(dp):  # function for registration of support functions/handlers

    dp.register_message_handler(cb_cancel, commands=['cancel'], state='*')
    dp.register_message_handler(find_location, state=PriceStatesGroup.location)
    dp.register_callback_query_handler(check_in_calendar, simple_cal_callback.filter(),
                                       state=PriceStatesGroup.check_in)
    dp.register_callback_query_handler(check_out_calendar, simple_cal_callback.filter(),
                                       state=PriceStatesGroup.check_out)
    dp.register_message_handler(max_price_limit, state=PriceStatesGroup.cost_max)
    dp.register_message_handler(min_price_limit, state=PriceStatesGroup.cost_min)
    dp.register_message_handler(distance_limit, state=PriceStatesGroup.distance_max)
    dp.register_message_handler(result_limit, state=PriceStatesGroup.result_size)
    dp.register_callback_query_handler(load_photo, state=PhotoState.need_photo)
    dp.register_message_handler(photo_limit, state=PhotoState.photo_amount)
