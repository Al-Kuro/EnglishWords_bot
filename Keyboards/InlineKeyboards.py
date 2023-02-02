from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def hello_msg():
    keyboard = InlineKeyboardMarkup(row_width=1)
    one = InlineKeyboardButton(text='Подписаться', url='https://t.me/english_words_b')
    keyboard.add(one)

    return keyboard


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
    five = InlineKeyboardButton(text='C', callback_data='C')
    keyboard.add(one, two, three, four, five)
    text = '2. Какой у Вас уровень английского языка?'

    return text, keyboard


def choice_participate_rankings():
    keyboard = InlineKeyboardMarkup(row_width=2)
    one = InlineKeyboardButton(text='Да', callback_data='yes_rates')
    two = InlineKeyboardButton(text='Нет', callback_data='no_rates')
    keyboard.add(one, two)
    text = '3. Желаете ли Вы участвовать в таблице рейтинга?'

    return text, keyboard


def learn_words():
    keyboard = InlineKeyboardMarkup(row_width=1)
    one = InlineKeyboardButton(text='Далее', callback_data='learn')
    keyboard.add(one)

    return keyboard


def learn_words_continue(text):
    keyboard = InlineKeyboardMarkup(row_width=1)
    one = InlineKeyboardButton(text=text, callback_data='learn_continue')
    keyboard.add(one)

    return keyboard


def check_learn_word(one_word, two_word, three_word, four_word):
    keyboard = InlineKeyboardMarkup(row_width=1)
    one = InlineKeyboardButton(text=one_word, callback_data=one_word)
    two = InlineKeyboardButton(text=two_word, callback_data=two_word)
    three = InlineKeyboardButton(text=three_word, callback_data=three_word)
    four = InlineKeyboardButton(text=four_word, callback_data=four_word)
    keyboard.add(one, two, three, four)

    return keyboard


# Далее обработка 'Изменить анкету 📝' из главного меню
def change_form():
    keyboard = InlineKeyboardMarkup(row_width=1)
    one = InlineKeyboardButton(text='Уровень английского 👨‍🏫', callback_data='lvl_english_change')
    two = InlineKeyboardButton(text='Количество изучаемых слов в день 🔢', callback_data='words_count_change')
    three = InlineKeyboardButton(text='Участие в таблице рейтинга 📈', callback_data='table_rating_change')
    four = InlineKeyboardButton(text='Завершить редактирование ☑️', callback_data='change_form_close')
    keyboard.add(one, two, three, four)
    text = 'Выберите, что необходимо изменить ♻️'

    return text, keyboard


def change_form_lvl_english():
    keyboard = InlineKeyboardMarkup(row_width=3)
    one = InlineKeyboardButton(text='A1', callback_data='A1_change')
    two = InlineKeyboardButton(text='A2', callback_data='A2_change')
    three = InlineKeyboardButton(text='B1', callback_data='B1_change')
    four = InlineKeyboardButton(text='B2', callback_data='B2_change')
    five = InlineKeyboardButton(text='C', callback_data='C_change')
    keyboard.add(one, two, three, four, five)
    text = 'Выберите уровень владения английским языком 🇬🇧'

    return text, keyboard


def change_form_words_count_learn():
    keyboard = InlineKeyboardMarkup(row_width=3)
    one = InlineKeyboardButton(text='3', callback_data='3_change')
    two = InlineKeyboardButton(text='4', callback_data='4_change')
    three = InlineKeyboardButton(text='5', callback_data='5_change')
    keyboard.add(one, two, three)
    text = 'Выберите желаемое количество слов для изучения в день 📖'

    return text, keyboard


def change_form_table_rating():
    keyboard = InlineKeyboardMarkup(row_width=2)
    one = InlineKeyboardButton(text='Да ✔️', callback_data='yes_rates_change')
    two = InlineKeyboardButton(text='Нет ✖️', callback_data='no_rates_change')
    keyboard.add(one, two)
    text = 'Желаете ли Вы участвовать в таблице рейтинга? 📈'

    return text, keyboard


# Далее вывод Таблицы рейтинга
def table_rating_output(first_pg, second_pg, is_current_user, users):
    keyboard = InlineKeyboardMarkup(row_width=3)
    text = f'Таблица рейтинга 📊\n\n'
    num = 1
    if len(users) <= 10:
        for user in users:
            text += f'{num}. {user.user_name}: {user.score_table_rating} ' \
                    f'{"👨‍💻" if is_current_user == user.user_name else ""}\n'
            num += 1
        return text, keyboard
    # Вывод, если пользователей больше 10
    first = InlineKeyboardButton(text=f'{first_pg} ◀️', callback_data=f'{first_pg}_before_tablerating')
    close = InlineKeyboardButton(text='Закрыть ⏹', callback_data=f'close_table_rating')
    second = InlineKeyboardButton(text=f'{second_pg} ▶️', callback_data=f'{second_pg}_after_tablerating')
    if second_pg - first_pg == 2:
        users_lst = users[(first_pg * 10) + 1:(first_pg * 10) + 11]
    else:
        users_lst = users[first_pg:(second_pg * 5) + 1]
    if users_lst:
        for user in users_lst:
            text += f'{num}. {user.user_name}: {user.score_table_rating} ' \
                    f'{"👨‍💻" if is_current_user == user.user_name else ""}\n'
            num += 1
        if len(users_lst) < 10 and second_pg - first_pg == 2:
            keyboard.add(first, close)
        elif second_pg - first_pg == 2:
            keyboard.add(first, close, second)
        else:
            keyboard.add(close, second)

    return text, keyboard

