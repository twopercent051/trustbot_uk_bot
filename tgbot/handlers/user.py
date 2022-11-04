from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hbold
from aiogram.dispatcher import FSMContext

from tgbot.misc.states import FSMRegistration, FSMRequest, FSMConnection, FSMSettings
from tgbot.misc import checker
from tgbot.database import db_connector
from tgbot.keyboards import reply
from tgbot.keyboards import inline
from tgbot.config import load_config
from create_bot import bot


async def user_start(message: Message):
    text = [
        f'☀️ <b>Доброго времени суток</b>, бот создан, чтобы обрабатывать заявки и обращения пользователей. Чтобы',
        f'воспользоваться этим, пришлите для начала Ваше <b>Имя</b> и <b>Фамилию</b>'
    ]
    await FSMRegistration.name.set()
    await message.answer(' '.join(text))


async def get_user_name(message: Message, state: FSMContext):
    text_ok = [
        f'📞Теперь отправьте Ваш <b>номер телефона</b> через <b>+7</b> следующим сообщением:'
    ]
    text_error = [
        f'⛔️📛<b>Имя</b> и <b>Фамилия</b> должны быть введены через один <i>пробел</i>, и должны быть',
        f'написаны через <i>кириллицу</i>. Также должны быть <i>заглавные буквы</i>.',
        f'<b>Учтите формат и попробуйте снова:</b>'
    ]
    check_name = await checker.user_name_checker(str(message.text))
    if check_name:
        user_id = message.from_user.id
        try:
            username = message.from_user.username
        except:
            username = '---'
        async with state.proxy() as data:
            data['user_id'] = user_id
            data['user_username'] = username
            data['user_name'] = message.text
        await FSMRegistration.next()
        await message.answer(' '.join(text_ok))
    else:
        await message.answer(' '.join(text_error))


async def main_menu_by_message(message: Message):
    text_ok = [
        f'✈️<b>Добро пожаловать</b> <i>в главное меню чат-бота Управляющей компании "УЭР-ЮГ"</i>. Здесь',
        f'Вы можете оставить заявку для управляющей компании или направить свое предложение по управлению домом.',
        f'Просто воспользуйтесь кнопками <b><i>меню</i></b>, чтобы взаимодействовать с функциями бота:'
    ]
    await FSMRegistration.main.set()
    await message.answer(' '.join(text_ok), reply_markup=reply.main_menu_user_keyboard)
    print(message.chat.id)


async def main_menu_by_callback(callback: CallbackQuery):
    text_ok = [
        f'✈️<b>Добро пожаловать</b> <i>в главное меню чат-бота Управляющей компании "УЭР-ЮГ"</i>. Здесь',
        f'Вы можете оставить заявку для управляющей компании или направить свое предложение по управлению домом.',
        f'Просто воспользуйтесь кнопками <b><i>меню</i></b>, чтобы взаимодействовать с функциями бота:'
    ]
    await FSMRegistration.main.set()
    await callback.message.answer(' '.join(text_ok), reply_markup=reply.main_menu_user_keyboard)
    await bot.answer_callback_query(callback.id)


async def get_user_phone(message: Message, state: FSMContext):
    text_error = [
        f'⛔️📛⛔{hbold("Номер телефона")} должен содержать 11 цифр и должен обязательно содержать в начале',
        f'{hbold("+7. Учтите формат и попробуйте снова:")}'
    ]
    check_phone = await checker.user_phone_checker(str(message.text))
    if check_phone:
        async with state.proxy() as data:
            data['user_phone'] = message.text
            data['is_blocked'] = 'False'
        await db_connector.sql_add_user(state)
        await state.finish()
        await main_menu_by_message(message)
    else:
        await message.answer(' '.join(text_error))


async def request_category_by_message(message: Message):
    text = [
        '📛👇📛<i>Выберите категорию, по которой Вы хотите оставить заявку в УК:</i>'
    ]
    await FSMRequest.request_main.set()
    await message.answer(text=' '.join(text), reply_markup=inline.main_request_keyboard)


async def request_category_by_callback(callback: CallbackQuery):
    text = [
        '📛👇📛<i>Выберите категорию, по которой Вы хотите оставить заявку в УК:</i>'
    ]
    await FSMRequest.request_main.set()
    await callback.message.answer(text=' '.join(text), reply_markup=inline.main_request_keyboard)
    await bot.answer_callback_query(callback.id)


async def request_adress(callback: CallbackQuery):
    text = [
        '<i><b>Шаг 1/3.</b></i> 📝Напишите адрес или ориентир проблемы (улицу, номер дома, подъезд, этаж и квартиру)',
        'или пропустите этот пункт:'
    ]
    await FSMRequest.request_adress.set()
    await callback.message.answer(text=' '.join(text), reply_markup=inline.pass_keyboard)
    await bot.answer_callback_query(callback.id)


async def request_photo_by_message(message: Message, state: FSMContext):
    text = [
        '<b><i>Шаг 2/3.</i></b> 🖼Прикрепите фотографию или видео к своей заявке или пропустите этот пункт:'
    ]
    user_id = message.from_user.id
    user_adress = message.text
    async with state.proxy() as data:
        data['user_id'] = user_id
        data['user_adress'] = user_adress
    await FSMRequest.request_photo.set()
    await message.answer(' '.join(text), reply_markup=inline.pass_keyboard)


async def request_photo_by_callback(callback: CallbackQuery, state: FSMContext):
    text = [
        '<b><i>Шаг 2/3.</i></b> 🖼Прикрепите фотографию или видео к своей заявке или пропустите этот пункт:'
    ]
    user_adress = ''
    async with state.proxy() as data:
        data['user_id'] = callback.from_user.id
        data['user_adress'] = user_adress
    await FSMRequest.request_photo.set()
    await callback.message.answer(text=' '.join(text), reply_markup=inline.pass_keyboard)
    await bot.answer_callback_query(callback.id)


async def request_desc_by_message_success(message: Message, state: FSMContext):
    text = [
        '<b><i>Шаг 3/3.</i></b> 📛Напишите причину обращения в подробностях:'
    ]
    try:
        file_id = message.video.file_id
    except:
        file_id = message.photo[0].file_id
    async with state.proxy() as data:
        data['file_id'] = file_id
    await FSMRequest.request_description.set()
    await message.answer(text=' '.join(text), reply_markup=inline.back_keyboard)


async def request_desc_by_message_fail(message: Message):
    text = [
        '⛔️📛В данном пункте нужно обязательно отправить <b>фотографию</b> или <b>видео</b> в виде медиа-сообщения.',
        '<b><i>Попробуйте ещё раз:</i></b>'
    ]
    await message.answer(text=' '.join(text), reply_markup=inline.back_keyboard)


async def request_desc_by_callback(callback: CallbackQuery, state: FSMContext):
    text = [
        '<b><i>Шаг 3/3.</i></b> 📛Напишите причину обращения в подробностях:'
    ]
    file_id = None
    async with state.proxy() as data:
        data['file_id'] = file_id
    await FSMRequest.request_description.set()
    await callback.message.answer(text=' '.join(text))
    await bot.answer_callback_query(callback.id)


async def request_finish(message: Message, state: FSMContext):
    text = [
        '✅<b>Жалоба отправлена администрации.</b> <i>Спасибо за ваше обращение!</i>'
    ]
    config = load_config(".env")
    async with state.proxy() as data:
        request_group_id = config.misc.request_group
        user_id = data.as_dict()['user_id']
        user_adress = data.as_dict()['user_adress']
        file_id = data.as_dict()['file_id']
        db_response = await db_connector.get_user_by_id(user_id)
        user_username = db_response[0]
        user_name = db_response[1]
        user_phone = db_response[2]
        if len(user_username) > 0:
            user_username = '@' + user_username
        text_admin = [
            '⛔️<b>Поступила жалоба:</b>',
            user_username,
            f'<b><i>Имя и Фамилия:</i></b> {user_name}',
            f'<b><i>Номер телефона:</i></b> {user_phone}',
            f'<b><i>Адрес:</i></b> {user_adress}',
            f'<b><i>Содержание:</i></b> {message.text}'
        ]
        if file_id is not None:
            try:
                await bot.send_photo(chat_id=request_group_id, photo=file_id, caption='\n'.join(text_admin))
            except:
                await bot.send_video(chat_id=request_group_id, video=file_id, caption='\n'.join(text_admin))
        else:
            await bot.send_message(chat_id=request_group_id, text='\n'.join(text_admin))
        await state.finish()
        await message.answer(' '.join(text))


async def request_offer(callback: CallbackQuery):
    text = [
        '💡<b><i>Распишите Ваше предложение в подробностях: (Добавьте фотографию если есть)</i></b>'
    ]
    await FSMRequest.offer_description.set()
    await callback.message.answer(text=' '.join(text), reply_markup=inline.back_keyboard)
    await bot.answer_callback_query(callback.id)


async def offer_finish(message: Message):
    config = load_config(".env")
    offer_group_id = config.misc.offer_group
    text_to_user = ['✅💡Идея принята и передана администрации. Спасибо за Ваше обращение!']
    user_id = message.from_user.id
    db_response = await db_connector.get_user_by_id(user_id)
    user_username = db_response[0]
    user_name = db_response[1]
    user_phone = db_response[2]
    if len(user_username) > 0:
        user_username = '@' + user_username
    cont_type = message.content_type
    if cont_type == 'text':
        text_to_admin = [
            '💡️<b>Поступило новое предложение:</b>',
            user_username,
            f'<b><i>Имя и Фамилия:</i></b> {user_name}',
            f'<b><i>Номер телефона:</i></b> {user_phone}',
            f'<b><i>Содержание:</i></b> {message.text}'
        ]
        await bot.send_message(chat_id=offer_group_id, text='\n'.join(text_to_admin))
        await message.answer(' '.join(text_to_user))
    else:
        text_to_admin = [
            '💡️<b>Поступило новое предложение:</b>',
            user_username,
            f'<b><i>Имя и Фамилия:</i></b> {user_name}',
            f'<b><i>Номер телефона:</i></b> {user_phone}',
            f'<b><i>Содержание:</i></b> {message.caption}'
        ]
        if cont_type == 'photo':
            file_id = message.photo[0].file_id
            await bot.send_photo(chat_id=offer_group_id, photo=file_id, caption='\n'.join(text_to_admin))
        if cont_type == 'audio':
            file_id = message.audio.file_id
            await bot.send_audio(chat_id=offer_group_id, audio=file_id, caption='\n'.join(text_to_admin))
        if cont_type == 'video':
            file_id = message.video.file_id
            await bot.send_video(chat_id=offer_group_id, video=file_id, caption='\n'.join(text_to_admin))
        await message.answer(' '.join(text_to_user))


async def contact_info(message: Message):
    text = [
        '<u>Управляющая компания:</u>',
        '<b>Диспетчерская служба ООО "УЭР-ЮГ"</b>',
        '+7 4722 35-50-06',
        '<b>Инженеры ООО "УЭР-ЮГ"</b>',
        '+7 920 566-28-86',
        '<b>Бухгалтерия ООО "УЭР-ЮГ"</b>',
        '+7 4722 35-50-06',
        '<i>Белгород, Свято-Троицкий б-р, д. 15, подъезд No 1</i>',
        '',
        '<u>Телефоны для открытия ворот и шлагбаума:</u>',
        '<b>Шлагбаум "Набережная"</b>',
        '+7 920 554-87-74',
        '<b>Ворота "Харьковские"</b>',
        '+7920 554-87-40',
        '<b>Ворота "Мост"</b>',
        '+7 920 554-64-06',
        '<b>Калитка 1 "Мост"</b>',
        '+7 920 554-42-10',
        '<b>Калитка 2 "Мост"</b>',
        '+7 920 554-89-04',
        '<b>Калитка 3 "Харьковская"</b>',
        '+7 920 554-87-39',
        '<b>Калитка 4 "Харьковская"</b>',
        '+7 920 554-89-02',
        '',
        '<b>Охрана</b>',
        '+7 915 57-91-457',
        '',
        '<b>Участковый</b>',
        'Куленцова Марина Владимировна',
        '+7 999 421-53-72'
    ]
    await message.answer('\n'.join(text))


async def connection_method(message: Message):
    text = [
        '👇Выберите способ связи из нижеперечисленного списка:'
    ]
    await FSMConnection.connection_method.set()
    await message.answer(text=' '.join(text), reply_markup=inline.connection_method_keyboard)


async def phone_confirm(callback: CallbackQuery):
    user_id = callback.from_user.id
    phone = await db_connector.get_phone(user_id)
    text = [
        f'<b>Это Ваш верный номер телефона</b> {phone}? <i>Если да, нажмите соответствующую кнопку, <b>если нет,</b></i>',
        'впишите свой актуальный номер телефона здесь'
    ]
    await FSMConnection.connection_confirm.set()
    await callback.message.answer(text=' '.join(text), reply_markup=inline.yes_keyboard)
    await bot.answer_callback_query(callback.id)


async def change_phone_by_connection(message: Message):
    text = [
        '🛠✅🛠Настройки номера успешно применены!'
    ]
    text_error = [
        f'⛔️📛⛔<b>Номер телефона</b> должен содержать 11 цифр и должен обязательно содержать в начале',
        f'<b>+7. Учтите формат и попробуйте снова:</b>'
    ]
    check_phone = await checker.user_phone_checker(str(message.text))
    if check_phone:
        user_id = message.from_user.id
        await db_connector.change_phone(user_id=user_id, new_phone=message.text)
        await message.answer(text=' '.join(text))
        phone = await db_connector.get_phone(user_id)
        text = [
            f'<b>Это Ваш верный номер телефона</b> {phone}? <i>Если да, нажмите соответствующую кнопку, <b>если нет,</b></i>',
            'впишите свой актуальный номер телефона здесь'
        ]
        await FSMConnection.connection_confirm.set()
        await message.answer(text=' '.join(text), reply_markup=inline.yes_keyboard)
    else:
        await message.answer(' '.join(text_error))


async def get_call_offer(callback: CallbackQuery):
    config = load_config(".env")
    admin_group_id = config.misc.admin_group
    text_to_user = ['✅Отлично! Наш диспетчер перезвонит Вам в ближайшее время.']
    user_id = callback.from_user.id
    db_response = await db_connector.get_user_by_id(user_id)
    user_username = db_response[0]
    user_name = db_response[1]
    user_phone = db_response[2]
    if len(user_username) > 0:
        user_username = '@' + user_username
    text_to_admin = [
        '💡️<b>Поступил запрос на звонок:</b>',
        user_username,
        f'<b><i>Имя и Фамилия:</i></b> {user_name}',
        f'<b><i>Номер телефона:</i></b> {user_phone}'
    ]
    await bot.send_message(chat_id=admin_group_id, text='\n'.join(text_to_admin))
    await callback.message.answer(' '.join(text_to_user))
    await bot.answer_callback_query(callback.id)


async def start_dialog(callback: CallbackQuery):
    text = [
        '✅📞✅Добрый день! Я - диспетчер управляющей компании "УЭР-ЮГ", готов помочь Вам. Напишите, пожалуйста',
        'интересующий Вас вопрос и ожидайте'
    ]
    await FSMConnection.operator_dialog.set()
    await callback.message.answer(text=' '.join(text), reply_markup=inline.close_dialog_keyboard)
    await bot.answer_callback_query(callback.id)


async def message_to_operator(message: Message):
    config = load_config(".env")
    admin_group_id = config.misc.admin_group
    user_id = message.from_user.id
    db_response = await db_connector.get_user_by_id(user_id)
    user_username = db_response[0]
    user_name = db_response[1]
    user_phone = db_response[2]
    if len(user_username) > 0:
        user_username = '@' + user_username
    text_to_admin = [
        '✉️<b>Сообщение от пользователя:</b>',
        f'{user_username} [{user_id}]',
        f'<b><i>Имя и Фамилия:</i></b> {user_name}',
        f'<b><i>Номер телефона:</i></b> {user_phone}',
        f'<b><i>Текст сообщения:</i></b> {message.text}',
        '',
        '<b>Для ответа используйте "Ответить на сообщение"</b>'
    ]
    await bot.send_message(chat_id=admin_group_id, text='\n'.join(text_to_admin))


async def finish_dialog(callback: CallbackQuery):
    text = [
        '❌📞Диалог с администратором завершён...'
    ]
    await FSMRegistration.main.set()
    await callback.message.answer(text=' '.join(text))
    await bot.answer_callback_query(callback.id)


async def choice_settings(message: Message):
    text = [
        '⚙Тут Вы сможете поменять <b>Имя</b> и <b>Фамилию</b> в Базе данных нашего бота или же поменять Ваш',
        '<b>номер телефона</b>, если Вы изначально вводили что-то неверно. Выберите, что хотите поменять или',
        'вернитесь назад в <b><i>главное меню:</i></b>'
    ]
    await FSMSettings.settings_choice.set()
    await message.answer(text=' '.join(text), reply_markup=inline.choice_settings_keyboard)


async def change_name_start(callback: CallbackQuery):
    text = [
        '🛠<i>Отправьте своё Имя и Фамилию, чтобы поменять настройки:</i>'
    ]
    await FSMSettings.settings_name.set()
    await callback.message.answer(text=' '.join(text))
    await bot.answer_callback_query(callback.id)


async def change_name_finish(message: Message):
    text_ok = [
        '🛠✅🛠Настройки имени успешно применены!'
    ]
    text_error = [
        f'⛔️📛<b>Имя</b> и <b>Фамилия</b> должны быть введены через один <i>пробел</i>, и должны быть',
        f'написаны через <i>кириллицу</i>. Также должны быть <i>заглавные буквы</i>.',
        f'<b>Учтите формат и попробуйте снова:</b>'
    ]
    check_name = await checker.user_name_checker(str(message.text))
    if check_name:
        user_id = message.from_user.id
        await db_connector.change_name(user_id=user_id, new_name=message.text)
        await FSMRegistration.main.set()
        await message.answer(text=' '.join(text_ok))
    else:
        await message.answer(' '.join(text_error))


async def change_phone_start(callback: CallbackQuery):
    text = [
        '🛠<i>Отправьте свой номер телефона, чтобы поменять настройки:</i>'
    ]
    await FSMSettings.settings_phone.set()
    await callback.message.answer(text=' '.join(text))
    await bot.answer_callback_query(callback.id)


async def change_phone_finish(message: Message):
    text_ok = [
        '🛠✅🛠Настройки номера успешно применены!'
    ]
    text_error = [
        f'⛔️📛⛔<b>Номер телефона</b> должен содержать 11 цифр и должен обязательно содержать в начале',
        f'<b>+7. Учтите формат и попробуйте снова:</b>'
    ]
    check_phone = await checker.user_phone_checker(str(message.text))
    if check_phone:
        user_id = message.from_user.id
        await db_connector.change_phone(user_id=user_id, new_phone=message.text)
        await FSMRegistration.main.set()
        await message.answer(text=' '.join(text_ok))
    else:
        await message.answer(' '.join(text_error))


async def you_are_blocked_by_message(message: Message):
    text = [
        '❌❌❌ВЫ ЗАБЛОКИРОВАНЫ!',
        'Обратитесь к администратору'
    ]
    await message.answer('\n'.join(text))


async def you_are_blocked_by_callback(callback: CallbackQuery):
    text = [
        '❌❌❌ВЫ ЗАБЛОКИРОВАНЫ!',
        'Обратитесь к администратору'
    ]
    await callback.message.answer('\n'.join(text))


def register_user(dp: Dispatcher):
    dp.register_message_handler(you_are_blocked_by_message, state='*', is_blocked=True)
    dp.register_message_handler(user_start, commands=["start"], state='*', is_loged=False)
    dp.register_message_handler(main_menu_by_message, commands=["start"], state='*', is_loged=True)
    dp.register_message_handler(get_user_name, content_types=['text'], state=FSMRegistration.name)
    dp.register_message_handler(get_user_phone, content_types=['text'], state=FSMRegistration.phone)
    dp.register_message_handler(request_category_by_message, Text(equals='📛Оставить заявку'), state='*')
    dp.register_message_handler(request_photo_by_message, content_types=['text'], state=FSMRequest.request_adress)
    dp.register_message_handler(request_desc_by_message_success, content_types=['photo', 'video'],
                                state=FSMRequest.request_photo)
    dp.register_message_handler(request_desc_by_message_fail, state=FSMRequest.request_photo)
    dp.register_message_handler(request_finish, state=FSMRequest.request_description)
    dp.register_message_handler(offer_finish, content_types=['text', 'video', 'photo'],
                                state=FSMRequest.offer_description)
    dp.register_message_handler(contact_info, Text(equals='☎️Полезные контакты'), state='*')
    dp.register_message_handler(connection_method, Text(equals='📞Связаться'), state='*')
    dp.register_message_handler(change_phone_by_connection, content_types=['text'],
                                state=FSMConnection.connection_confirm)
    dp.register_message_handler(message_to_operator, content_types=['text'], state=FSMConnection.operator_dialog)
    dp.register_message_handler(choice_settings, Text(equals='⚙️Настройки'), state='*')
    dp.register_message_handler(change_name_finish, content_types=['text'], state=FSMSettings.settings_name)
    dp.register_message_handler(change_phone_finish, content_types=['text'], state=FSMSettings.settings_phone)

    dp.register_callback_query_handler(you_are_blocked_by_callback, state='*', is_blocked=True)
    dp.register_callback_query_handler(main_menu_by_callback, lambda x: x.data == 'back', state=FSMRequest.request_main)
    dp.register_callback_query_handler(request_offer, lambda x: x.data == 'share_offer', state=FSMRequest.request_main)
    dp.register_callback_query_handler(request_adress, lambda x: x.data == 'leave_req', state=FSMRequest.request_main)
    dp.register_callback_query_handler(request_photo_by_callback, lambda x: x.data == 'pass',
                                       state=FSMRequest.request_adress)
    dp.register_callback_query_handler(request_category_by_callback, lambda x: x.data == 'back',
                                       state=FSMRequest.request_adress)
    dp.register_callback_query_handler(request_desc_by_callback, lambda x: x.data == 'pass',
                                       state=FSMRequest.request_photo)
    dp.register_callback_query_handler(request_adress, lambda x: x.data == 'back', state=FSMRequest.request_photo)
    dp.register_callback_query_handler(request_photo_by_callback, lambda x: x.data == 'back',
                                       state=FSMRequest.request_description)
    dp.register_callback_query_handler(request_category_by_callback, lambda x: x.data == 'back',
                                       state=FSMRequest.offer_description)
    dp.register_callback_query_handler(main_menu_by_callback, lambda x: x.data == 'back',
                                       state=FSMConnection.connection_method)
    dp.register_callback_query_handler(phone_confirm, lambda x: x.data == 'call_me',
                                       state=FSMConnection.connection_method)
    dp.register_callback_query_handler(get_call_offer, lambda x: x.data == 'yes',
                                       state=FSMConnection.connection_confirm)
    dp.register_callback_query_handler(start_dialog, lambda x: x.data == 'write_me',
                                       state=FSMConnection.connection_method)
    dp.register_callback_query_handler(finish_dialog, lambda x: x.data == 'close_dialog',
                                       state=FSMConnection.operator_dialog)
    dp.register_callback_query_handler(main_menu_by_callback, lambda x: x.data == 'back',
                                       state=FSMSettings.settings_choice)
    dp.register_callback_query_handler(change_name_start, lambda x: x.data == 'change_name',
                                       state=FSMSettings.settings_choice)
    dp.register_callback_query_handler(change_phone_start, lambda x: x.data == 'change_phone',
                                       state=FSMSettings.settings_choice)
