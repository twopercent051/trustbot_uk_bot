from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

from tgbot.config import load_config
from tgbot.misc.states import FSMAdmin
from tgbot.keyboards import inline
from tgbot.database import db_connector
from create_bot import bot

import asyncio

config = load_config(".env")
admin_group = config.misc.admin_group
admin_chats = [
    config.misc.request_group,
    config.misc.offer_group,
    config.misc.admin_group
]


async def answer_to_user(message: Message):
    user_message = message.reply_to_message.text
    try:
        user_id = int(user_message.split('\n')[1].split(' ')[-1][1:][:-1])
        await bot.send_message(chat_id=user_id, text=message.text)
    except:
        text = ['Невозможно ответить пользователю. Проверьте входящее сообщение']
        await message.answer(''.join(text))


async def main_menu_by_message(message: Message, state: FSMContext):
    state_name = await state.get_state()
    print(state_name)
    text = [
        'Это админ-панель администратора. Здесь Вы можете сделать массовую рассылку и получить информацию по',
        'пользователям, а также блокировать и разблокировать пользователей.'
    ]
    await FSMAdmin.main.set()
    await message.answer(text=' '.join(text), reply_markup=inline.admin_main_menu_keyboard)


async def main_menu_by_callback(callback: CallbackQuery):
    text = [
        'Это админ-панель администратора. Здесь Вы можете сделать массовую рассылку и получить информацию по',
        'пользователям, а также блокировать и разблокировать пользователей.'
    ]
    await FSMAdmin.main.set()
    await callback.message.answer(text=' '.join(text), reply_markup=inline.admin_main_menu_keyboard)
    await bot.answer_callback_query(callback.id)


async def mailing_start(callback: CallbackQuery):
    text = [
        'Введите сообщение для рассылки. Оно будет отправлено всем зарегистрированным пользователям или вернитесь назад'
    ]
    await FSMAdmin.mailing.set()
    await callback.message.answer(text=' '.join(text), reply_markup=inline.back_keyboard)
    await bot.answer_callback_query(callback.id)


async def mailing_finish(message: Message):
    mailing_text = message.text
    list_users = await db_connector.get_users()
    for user_id in list_users:
        await bot.send_message(chat_id=user_id, text=mailing_text)
        await asyncio.sleep(1)
    text_to_admin = [
        f'Успешно разослали текст по {len(list_users)} пользователям!'
    ]
    await message.answer(' '.join(text_to_admin), reply_markup=inline.home_keyboard)


async def get_user_info_start(callback: CallbackQuery):
    text = [
        'Введите Имя, Фамилию, номер телефона (начиная с +7), user_id или user_name(начиная с @)'
    ]
    await FSMAdmin.user_info.set()
    await callback.message.answer(text=' '.join(text), reply_markup=inline.home_keyboard)
    await bot.answer_callback_query(callback.id)


async def get_user_info_finish(message: Message):
    user_list = await db_connector.find_user(message.text)
    text_title = [
        f'По запросу найдено {len(user_list)} записей:'
    ]
    await message.answer(' '.join(text_title))
    for user in user_list:
        if user[4] == 'False':
            is_blocked = 'Пользователь не заблокирован'
        else:
            is_blocked = 'Пользователь в чёрном списке'
        if len(user[1]) > 0:
            user_name = f'@{user[1]}'
        else:
            user_name = ''
        user_text = [
            f'<b>Имя, Фамилия:</b> <i>{user[2]}</i>',
            f'<b>Телефон:</b> <i>{user[3]}</i>',
            f'<b>Username:</b> <i>{user_name}</i>',
            f'<b>User_id:</b> <i>{user[0]}</i>',
            is_blocked
        ]
        await message.answer(text='\n'.join(user_text))
    await message.answer('<b>Возврат в меню:</b>', reply_markup=inline.home_keyboard)


async def block_choice(callback: CallbackQuery):
    text = ['Выберите действие:']
    await FSMAdmin.block_choice.set()
    await callback.message.answer(text=' '.join(text), reply_markup=inline.block_menu_keyboard)
    await bot.answer_callback_query(callback.id)


async def block_user_start(callback: CallbackQuery):
    text = [
        'Введите id пользователя, которго хотите заблокировать. ID можно получить запросив инфомацию о',
        'пользователях в главном меню'
    ]
    await FSMAdmin.block_user.set()
    await callback.message.answer(text=' '.join(text), reply_markup=inline.home_keyboard)
    await bot.answer_callback_query(callback.id)


async def block_user_finish(message: Message):
    user_id = message.text
    await db_connector.block_user(user_id=user_id, is_blocking='True')
    user_name = await db_connector.get_name(user_id)
    text = [f'Пользователь <b>{user_name}</b> [{user_id}] заблокирован']
    await message.answer(text=' '.join(text), reply_markup=inline.home_keyboard)


async def unlock_user_start(callback: CallbackQuery):
    text = ['<b>Список заблокированных пользователей:</b>']
    blocked_users = await db_connector.blocked_users()
    for user in blocked_users:
        text.append(f'{user[1]} [{user[0]}]')
    text.append('<b>Отправьте id пользователя, которого нужно заблокировать</b>')
    if len(blocked_users) == 0:
        text = ['Нет заблокированных пользователей']
    await FSMAdmin.unblock_user.set()
    await callback.message.answer(text='\n'.join(text), reply_markup=inline.home_keyboard)
    await bot.answer_callback_query(callback.id)


async def unlock_user_finish(message: Message):
    user_id = message.text
    await db_connector.block_user(user_id=user_id, is_blocking='False')
    user_name = await db_connector.get_name(user_id)
    text = [f'Пользователь <b>{user_name}</b> [{user_id}] разблокирован']
    await message.answer(text=' '.join(text), reply_markup=inline.home_keyboard)


def register_admin(dp: Dispatcher):
    dp.register_message_handler(mailing_finish, state=FSMAdmin.mailing, content_types=['text'])
    dp.register_message_handler(main_menu_by_message, commands=['start'], chat_id=admin_group, state='*')
    dp.register_message_handler(answer_to_user, state="*", is_reply=True, chat_id=admin_group)
    dp.register_message_handler(get_user_info_finish, content_types=['text'], state=FSMAdmin.user_info)
    dp.register_message_handler(block_user_finish, content_types=['text'], state=FSMAdmin.block_user)
    dp.register_message_handler(unlock_user_finish, content_types=['text'], state=FSMAdmin.unblock_user)

    dp.register_callback_query_handler(mailing_start, lambda x: x.data == 'mailing', state=FSMAdmin.main)
    dp.register_callback_query_handler(main_menu_by_callback, lambda x: x.data == 'back', state=FSMAdmin.mailing)
    dp.register_callback_query_handler(main_menu_by_callback, lambda x: x.data == 'home', state='*')
    dp.register_callback_query_handler(get_user_info_start, lambda x: x.data == 'info_user', state=FSMAdmin.main)
    dp.register_callback_query_handler(block_choice, lambda x: x.data == 'block', state=FSMAdmin.main)
    dp.register_callback_query_handler(block_user_start, lambda x: x.data == 'block_user', state=FSMAdmin.block_choice)
    dp.register_callback_query_handler(unlock_user_start, lambda x: x.data == 'unlock_user',
                                       state=FSMAdmin.block_choice)
