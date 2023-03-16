from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_kb_start() -> ReplyKeyboardMarkup:  # start keyboard
    kb_start = ReplyKeyboardMarkup(resize_keyboard=True)
    kb_start.add(KeyboardButton('/lowprice')).insert(KeyboardButton('/highprice')).insert(KeyboardButton('/bestdeal'))
    return kb_start


def cancel_button() -> ReplyKeyboardMarkup:  # cancel kb
    cancel_b = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_b.add(KeyboardButton('/cancel'))
    return cancel_b


def need_photos(hotel_id) -> InlineKeyboardMarkup:  # photo need kb
    photo_kb = InlineKeyboardMarkup(row_width=2)
    photo_kb.add(InlineKeyboardButton('Yes, sure!', callback_data=f'Yes, {hotel_id}',),
                 InlineKeyboardButton('No, thanks', callback_data=f"No, {hotel_id}"))
    return photo_kb

