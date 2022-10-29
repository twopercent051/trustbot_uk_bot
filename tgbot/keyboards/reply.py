from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

leave_request_button = KeyboardButton('📛Оставить заявку')
connect_button = KeyboardButton('📞Связаться')
settings_button = KeyboardButton('⚙️Настройки')
useful_contacts_button = KeyboardButton('☎️Полезные контакты')
share_an_offer_button = KeyboardButton('💡Поделиться предложением')
back_button = KeyboardButton('⬅️Назад')
pass_button = KeyboardButton('▶Пропустить')
mailing_button = KeyboardButton('✉️Рассылка всем пользователям')
info_user_button = KeyboardButton('🗄📂Информация о пользователях')
block_button = KeyboardButton('❌❌Блокировка пользователей')

main_menu_user_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True). \
    add(leave_request_button).insert(connect_button).row(settings_button, useful_contacts_button)
main_menu_admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(mailing_button). \
    row(info_user_button, block_button)
