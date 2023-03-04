from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# def get_confirm_cancel_ikb() -> ReplyKeyboardMarkup:
#     ikb = ReplyKeyboardMarkup(resize_keyboard=True)
#     ikb.add(KeyboardButton('Confirm')).insert(KeyboardButton('Cancel all'))
#     return ikb


def get_kb_start() -> ReplyKeyboardMarkup:
    kb_start = ReplyKeyboardMarkup(resize_keyboard=True)
    kb_start.add(KeyboardButton('/lowprice')).insert(KeyboardButton('/highprice')).insert(KeyboardButton('/bestdeal'))
    return kb_start


def cancel_button() -> ReplyKeyboardMarkup:
    cancel_b = ReplyKeyboardMarkup(resize_keyboard=True)
    cancel_b.add(KeyboardButton('/cancel'))
    return cancel_b


def need_photos(hotel_id) -> InlineKeyboardMarkup:
    photo_kb = InlineKeyboardMarkup(row_width=2)
    photo_kb.add(InlineKeyboardButton('Yes, sure!', callback_data=f'Yes, {hotel_id}',),
                 InlineKeyboardButton('No, thanks', callback_data=f"No, {hotel_id}"))
    return photo_kb


def get_results_kb() -> ReplyKeyboardMarkup:
    results_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    results_kb.add(KeyboardButton('Show results'))
    return results_kb

