from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMRegistration(StatesGroup):
    name = State()
    phone = State()
    main = State()


class FSMRequest(StatesGroup):
    request_main = State()
    request_start = State()
    request_adress = State()
    request_photo = State()
    request_description = State()
    offer_description = State()


class FSMConnection(StatesGroup):
    connection_method = State()
    connection_confirm = State()
    operator_dialog = State()
    finish_dialog = State()


class FSMSettings(StatesGroup):
    settings_choice = State()
    settings_name = State()
    settings_phone = State()


class FSMAdmin(StatesGroup):
    main = State()
    mailing = State()
    user_info = State()
    block_choice = State()
    block_user = State()
    unblock_user = State()
