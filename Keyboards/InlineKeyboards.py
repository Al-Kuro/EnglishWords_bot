from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def fill_form_start():
    keyboard = InlineKeyboardMarkup(row_width=1)
    one = InlineKeyboardButton(text='Заполнить анкету', callback_data='form')
    keyboard.add(one)
    text = 'Вы приняты в канал!\nЗаполните анкету, которая определит ваши предпочтения по ' \
           'обучению'

    return text, keyboard


def choice_words_count():
    keyboard = InlineKeyboardMarkup(row_width=3)
    one = InlineKeyboardButton(text='3', callback_data='3')
    two = InlineKeyboardButton(text='4', callback_data='4')
    three = InlineKeyboardButton(text='5', callback_data='5')
    keyboard.add(one, two, three)
    text = '1. Сколько слов в день Вы хотите изучать?'

    return text, keyboard


def choice_level_english():
    keyboard = InlineKeyboardMarkup(row_width=3)
    one = InlineKeyboardButton(text='A1', callback_data='A1')
    two = InlineKeyboardButton(text='A2', callback_data='A2')
    three = InlineKeyboardButton(text='B1', callback_data='B1')
    four = InlineKeyboardButton(text='B2', callback_data='B2')
    five = InlineKeyboardButton(text='C1', callback_data='C1')
    six = InlineKeyboardButton(text='C2', callback_data='C2')
    keyboard.add(one, two, three, four, five, six)
    text = '2. Какой у Вас уровень английского языка?'

    return text, keyboard


def choice_participate_rankings():
    keyboard = InlineKeyboardMarkup(row_width=2)
    one = InlineKeyboardButton(text='Да', callback_data='yes_rates')
    two = InlineKeyboardButton(text='Нет', callback_data='no_rates')
    keyboard.add(one, two)
    text = '3. Желаете ли Вы участвовать в таблице лидеров?'

    return text, keyboard


def learn_words():
    keyboard = InlineKeyboardMarkup(row_width=1)
    one = InlineKeyboardButton(text='Далее', callback_data='learn')
    keyboard.add(one)

    return keyboard


def learn_words_end():
    keyboard = InlineKeyboardMarkup(row_width=1)
    one = InlineKeyboardButton(text='Готов!', callback_data='learn_end')
    keyboard.add(one)

    return keyboard
