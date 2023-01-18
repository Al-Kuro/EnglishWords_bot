from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

buttons_start = ['Учить слова 📖',
                 'Изменить анкету 📝',
                 'Таблица рейтинга 📊',
                 'Справка 📃',
                 'Полная версия 💹']


def get_start_keyboard():
    start_keyboard = ReplyKeyboardMarkup()
    for bt in buttons_start:
        start_keyboard.add(KeyboardButton(bt))

    return start_keyboard
