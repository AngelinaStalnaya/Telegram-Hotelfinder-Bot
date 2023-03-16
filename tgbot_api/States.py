from aiogram.dispatcher.filters.state import StatesGroup, State


class PriceStatesGroup(StatesGroup):  # FSMContext for user`s replies on commands

    sort = State()
    location = State()
    check_in = State()
    check_out = State()
    cost_max = State()
    cost_min = State()
    distance_max = State()
    result_size = State()


class PhotoState(StatesGroup):  # FSMContext for user`s replies on photo need

    need_photo = State()
    photo_amount = State()
