from datetime import date

from aiogram import Bot, Dispatcher, executor, types
import asyncio
import logging
import json
import random
from datetime import datetime

from aiogram.types import ContentType

from Keyboards import InlineKeyboards
from Keyboards import ReplyKeyboards
from utils import get_call_data_form

# Уровень логов и их вывод
logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)

# Чтение конфигурационного файла
with open(r'data\config.txt', 'r') as file:
    config = json.load(file)

# Создание экземпляра Бота
bot = Bot(config['token'])
dp = Dispatcher(bot)


async def check_subs_on_channel():
    while True:
        users = session.query(User).filter(User.user_state == 0).all()
        if users:
            for user in users:
                res = await bot.get_chat_member(-1001653709784, user.id_telegram)
                if res.status in ['member', 'creator']:
                    user.user_state = 1
                    if user.is_resubscribe:
                        user.is_resubscribe = False
                        user.user_state = 2
                        text = f'Ура! Вы снова с нами!'
                        await bot.delete_message(chat_id=user.id_telegram, message_id=user.start_msg)
                        await bot.send_message(chat_id=user.id_telegram, text=text)
                        continue
                    await bot.delete_message(chat_id=user.id_telegram, message_id=user.start_msg)
                    text, keyboard = InlineKeyboards.fill_form_start()
                    await bot.send_message(chat_id=user.id_telegram, text=text, reply_markup=keyboard)
            session.commit()
        users = session.query(User).filter(User.user_state == 2).all()
        if users:
            for user in users:
                res = await bot.get_chat_member(-1001653709784, user.id_telegram)
                if res.status not in ['member', 'creator']:
                    user.user_state = 0
                    user.is_resubscribe = True
                    text = 'Подпишитесь на канал, чтобы возобновить взаимодействие с Ботом'
                    keyboard = InlineKeyboards.hello_msg()
                    msg = await bot.send_message(chat_id=user.id_telegram, text=text, reply_markup=keyboard)
                    msg_id = msg.message_id
                    user.start_msg = msg_id
                    session.commit()

        await asyncio.sleep(5)


# Обработчик команды '/start'
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    is_user_exist = session.query(User).filter_by(id_telegram=message.from_user.id).first()
    if not is_user_exist:
        new_user = User(message.from_user.username, message.from_user.id)
        session.add(new_user)

        text = 'Добро пожаловать!\nДля взаимодействия с Ботом подпишитесь на канал по ссылке ниже:'
        keyboard = InlineKeyboards.hello_msg()
        msg = await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=keyboard)
        msg_id = msg.message_id
        new_user.start_msg = msg_id


# Обработчик инлайн анкетирования
@dp.callback_query_handler(lambda call: call.data in get_call_data_form()[1])
async def fill_form_call_logic(call: types.CallbackQuery):
    user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
    if user.user_state != 1:
        return

    form_separately = get_call_data_form()[0]
    form = form_separately[0]
    form_first_lst = form_separately[1]
    form_second_lst = form_separately[2]
    form_third_lst = form_separately[3]

    if call.data == form:
        await call.message.delete()
        text, keyboard = InlineKeyboards.choice_words_count()
        await call.message.answer(text=text, reply_markup=keyboard)

    elif call.data in form_first_lst:
        user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
        user.words_count_learn = call.data
        session.commit()

        await call.message.delete()
        text, keyboard = InlineKeyboards.choice_level_english()
        await call.message.answer(text=text, reply_markup=keyboard)

    elif call.data in form_second_lst:
        user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
        user.level_english_user = call.data
        session.commit()

        await call.message.delete()
        text, keyboard = InlineKeyboards.choice_participate_rankings()
        await call.message.answer(text=text, reply_markup=keyboard)

    elif call.data in form_third_lst:
        user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
        user.user_state = 2
        user.is_table_rating = True if call.data == 'yes_rates' else False
        session.commit()

        await call.message.delete()
        text = f'Анкета заполнена.\n' \
               f'Используйте меню для дальнейшего взаимодействия с ботом.'
        await call.message.answer(text=text, reply_markup=ReplyKeyboards.get_start_keyboard())


# Обработчик запоминания слов
@dp.callback_query_handler(lambda call: call.data == 'learn')
async def learn_words_call_logic(call: types.CallbackQuery):
    user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
    if user.user_state != 2:
        return

    await call.message.delete()

    user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
    current_words_to_learn = user.current_words_to_learn

    current_lst = []
    for lst in current_words_to_learn['current']:
        if lst[4] == 0 or lst[4] == 3:
            current_lst = lst
            break
    if not current_lst:
        text = f'Слова закончились\n' \
               f'Готовы проверить результат?'
        keyboard = InlineKeyboards.learn_words_continue('Погнали 🏃')
        await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=keyboard)

        lst_to_random = sorted(current_words_to_learn['current'], key=lambda a: random.random())
        user.current_words_to_learn = {'current': lst_to_random}

        # Изменяем состояние на 1
        user.today_words_str_state = 1
        session.commit()

        return

    word = current_lst[0]
    transcription = current_lst[1]
    translation = current_lst[2]
    audio = current_lst[3]
    # word_state = current_lst[4]
    text = f'<b>{word}</b>\n' \
           f'{transcription}\n\n' \
           f'{translation}'
    keyboard = InlineKeyboards.learn_words()
    await bot.send_voice(chat_id=call.from_user.id, voice=audio, caption=text, reply_markup=keyboard,
                         parse_mode='html')

    current_lst[4] = 1
    session.commit()
    user.current_words_to_learn = current_words_to_learn
    session.commit()


# Обработчик выбора варианта перевода
@dp.callback_query_handler(lambda call: call.data == 'learn_continue')
async def translate_words_call_logic(call: types.CallbackQuery):
    user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
    if user.user_state != 2:
        return

    await call.message.delete()

    user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
    current_words_to_learn = user.current_words_to_learn

    current_lst = []
    for lst in current_words_to_learn['current']:
        if lst[4] == 1:
            current_lst = lst
            break
    if not current_lst:
        right = 0
        incorrect = 0
        text = f'Ваш результат 👨‍💻 ({date.today()})\n\n'
        for lst in current_words_to_learn['current']:
            if lst[4] == 2:
                text += f'✅ {lst[0]} - {lst[2]}\n'
                right += 1
            if lst[4] == 3:
                text += f'❌ {lst[0]} - {lst[2]}\n'
                incorrect += 1
        if incorrect == 0:
            text += f'\nВау круто 🔥\n' \
                    f'Ты справился, молодец!'
        elif right >= incorrect:
            text += f'\nМолодец!\n' \
                    f'Но тебе еще есть чему поучиться'
        else:
            text += f'\nНе унывай! Больше практикуйся!'

        await bot.send_message(chat_id=call.from_user.id, text=text)

        user.current_words_to_learn = current_words_to_learn

        # Изменяем состояние на 2
        user.today_words_str_state = 2
        # Изменение слов в БД, в зависимости от верных/неверных ответов
        user_level = user.level_english_user
        user_words_dict = {'A1': user.A1_words,
                           'A2': user.A2_words,
                           'B1': user.B1_words,
                           'B2': user.B2_words,
                           'C': user.C_words}
        user_words = user_words_dict[user_level]

        for lst in current_words_to_learn['current']:
            if lst[4] == 2:  # Верный ответ
                user_words[lst[0]][4] = 2
            elif lst[4] == 3:  # Не верный ответ
                user_words[lst[0]][4] = 3

        session.commit()
        if user_level == 'A1':
            user.A1_words = user_words
        elif user_level == 'A2':
            user.A2_words = user_words
        elif user_level == 'B1':
            user.B1_words = user_words
        elif user_level == 'B2':
            user.B2_words = user_words
        elif user_level == 'C':
            user.C_words = user_words
        session.commit()

        return

    word = current_lst[0]
    transcription = current_lst[1]
    translate = current_lst[2]
    # word_state = current_lst[4]

    text = f'<b>{word}</b>\n' \
           f'{transcription}'

    # Получаем список слов для проверки из БД
    current_words_to_learn_check = user.current_words_to_learn_check['current_check']
    # Рандомно выбираем 3 слова (а всего их будет 4)
    three_words_to_check = sorted(current_words_to_learn_check,
                                  key=lambda a: random.random())[0:3]
    three_words_to_check.append(translate)
    four_words_to_check = sorted(three_words_to_check,
                                 key=lambda a: random.random())
    keyboard = InlineKeyboards.check_learn_word(*four_words_to_check)
    await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=keyboard, parse_mode='html')

    # Запись в БД 4 текущих слова, что были отправлены юзеру, как варианты ответа
    user.current_4lst_check = {'current_4lst_check': [*four_words_to_check],
                               'current_word': [word, transcription, translate]}
    session.commit()


# Обработчик верного/неверного варианта ответа
@dp.callback_query_handler(lambda call: call.data in session.query(User).
                           filter_by(id_telegram=call.from_user.id).
                           first().current_4lst_check['current_4lst_check'])
async def choice_right_incorrect_translate(call: types.CallbackQuery):
    user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
    if user.user_state != 2:
        return

    await call.message.delete()

    user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
    current_words_to_learn = user.current_words_to_learn
    current_4lst_check = user.current_4lst_check

    word = current_4lst_check['current_word'][0]
    transcription = current_4lst_check['current_word'][1]
    translate_true = current_4lst_check['current_word'][2]

    text = f'<b>{word}</b>\n' \
           f'{transcription}\n\n'

    is_right = False
    if call.data == translate_true:
        text += f'Верно ✅'
        is_right = True
    else:
        text += f'Неверно ❌\n' \
                f'Правильный ответ - {translate_true}'

    # Обновляем состояния верных/неверных ответов и прибавляем очки за каждый верный ответ
    lvl_english = user.level_english_user
    is_table_rating = user.is_table_rating
    for lst in current_words_to_learn['current']:
        if lst[0] == word:
            if is_right:  # Верный ответ
                lst[4] = 2
                if is_table_rating:  # Прибавляем очки за верный ответ
                    if lvl_english == 'A1':
                        user.score_table_rating += 0.5
                    elif lvl_english == 'A2':
                        user.score_table_rating += 1.0
                    elif lvl_english == 'B1':
                        user.score_table_rating += 1.5
                    elif lvl_english == 'B2':
                        user.score_table_rating += 2.0
                    elif lvl_english == 'C':
                        user.score_table_rating += 2.5
                    session.commit()
            else:  # Не верный ответ
                lst[4] = 3
            break
    session.commit()
    user.current_words_to_learn = current_words_to_learn
    session.commit()
    keyboard = InlineKeyboards.learn_words_continue('Далее 🙇‍♂️')
    await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=keyboard, parse_mode='html')


# Обработчик изменения анкеты
@dp.callback_query_handler(lambda call: call.data in ['lvl_english_change',
                                                      'words_count_change',
                                                      'table_rating_change',
                                                      'change_form_close'])
async def change_form(call: types.CallbackQuery):
    user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
    if user.user_state != 2:
        return

    await call.message.delete()

    if call.data == 'lvl_english_change':
        text, keyboard = InlineKeyboards.change_form_lvl_english()
        await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=keyboard)
    elif call.data == 'words_count_change':
        text, keyboard = InlineKeyboards.change_form_words_count_learn()
        await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=keyboard)
    elif call.data == 'table_rating_change':
        text, keyboard = InlineKeyboards.change_form_table_rating()
        await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=keyboard)
    elif call.data == 'change_form_close':
        text = 'Редактирование завершено ✅'
        await bot.send_message(chat_id=call.from_user.id, text=text)


# Обработчик изменения уровня английского языка
@dp.callback_query_handler(lambda call: call.data in ['A1_change',
                                                      'A2_change',
                                                      'B1_change',
                                                      'B2_change',
                                                      'C_change'])
async def change_form_lvl_engl(call: types.CallbackQuery):
    user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
    if user.user_state != 2:
        return

    await call.message.delete()

    user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
    if call.data == 'A1_change':
        user.level_english_user = 'A1'
    elif call.data == 'A2_change':
        user.level_english_user = 'A2'
    elif call.data == 'B1_change':
        user.level_english_user = 'B1'
    elif call.data == 'B2_change':
        user.level_english_user = 'B2'
    elif call.data == 'C_change':
        user.level_english_user = 'C'
    session.commit()

    text, keyboard = InlineKeyboards.change_form()
    await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=keyboard)


# Обработчик выбора количества изучаемых слов
@dp.callback_query_handler(lambda call: call.data in ['3_change',
                                                      '4_change',
                                                      '5_change'])
async def change_form_words_count(call: types.CallbackQuery):
    user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
    if user.user_state != 2:
        return

    await call.message.delete()

    user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
    if call.data == '3_change':
        user.words_count_learn = 3
    elif call.data == '4_change':
        user.words_count_learn = 4
    elif call.data == '5_change':
        user.words_count_learn = 5
    session.commit()

    text, keyboard = InlineKeyboards.change_form()
    await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=keyboard)


# Обработчик выбора участия в таблице рейтинга
@dp.callback_query_handler(lambda call: call.data in ['yes_rates_change',
                                                      'no_rates_change'])
async def change_form_table_rati(call: types.CallbackQuery):
    user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
    if user.user_state != 2:
        return

    await call.message.delete()

    user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
    if call.data == 'yes_rates_change':
        user.is_table_rating = True
    elif call.data == 'no_rates_change':
        user.is_table_rating = False
    session.commit()

    text, keyboard = InlineKeyboards.change_form()
    await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=keyboard)


# Обработчик пагинации страниц в таблице рейтинга
@dp.callback_query_handler(lambda call: '_tablerating' in call.data)
async def change_page_table_rating(call: types.CallbackQuery):
    user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
    if user.user_state != 2:
        return

    await call.message.delete()

    users = session.query(User).order_by(User.score_table_rating.desc()).all()
    user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
    is_current_user = user.user_name

    page = call.data.split('_')[0]
    first_pg = 0
    second_pg = 0
    next_page = call.data.split('_')[1]
    if next_page == 'before':
        if page == '1':
            first_pg = 1
            second_pg = int(page) + 1
        else:
            first_pg = int(page) - 1
            second_pg = int(page) + 1
    elif next_page == 'after':
        first_pg = int(page) - 1
        second_pg = int(page) + 1
    text, keyboard = InlineKeyboards.table_rating_output(first_pg=first_pg,
                                                         second_pg=second_pg,
                                                         is_current_user=is_current_user,
                                                         users=users)
    # Далее отправка сообщения
    await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=keyboard)


# Обработчик закрытия пагинации таблицы рейтинга
@dp.callback_query_handler(lambda call: call.data == 'close_table_rating')
async def close_table_rating(call: types.CallbackQuery):
    user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
    if user.user_state != 2:
        return

    await call.message.delete()


# Обработчик подготовки к оплате подписки
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query_handler(pre_checkout_q: types.PreCheckoutQuery):
    user = session.query(User).filter_by(id_telegram=pre_checkout_q.from_user.id).first()
    if user.user_state != 2:
        return

    await bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_q.id, ok=True)


# Обработчик успешного платежа
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    user = session.query(User).filter_by(id_telegram=message.from_user.id).first()
    if user.user_state != 2:
        return

    print('SUCCESSFUL PAYMENT:')
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f'{k} = {v}')

    text = f'Платеж на сумму {message.successful_payment.total_amount // 100}' \
           f'{message.successful_payment.currency} прошел успешно'
    await bot.send_message(chat_id=message.from_user.id,
                           text=text)


# Обработчик стартовой клавиатуры
@dp.message_handler(text=ReplyKeyboards.buttons_start)
async def hello(message: types.Message):
    user = session.query(User).filter_by(id_telegram=message.from_user.id).first()
    if user.user_state != 2:
        return

    if message.text == 'Учить слова 📖':
        user = session.query(User).filter_by(id_telegram=message.from_user.id).first()
        today_words_str = user.today_words_str

        # Проверка, был ли уже получен список слов для изучения на сегодня
        today_date_str = datetime.now().strftime("%Y-%m-%d")
        if today_date_str != today_words_str:
            user.today_words_str = datetime.now().strftime("%Y-%m-%d")
            user.today_words_str_state = 0
            session.commit()
        today_words_str_state = user.today_words_str_state
        if today_words_str_state == 1:
            text = f'Вы ранее получили список слов для изучения\n' \
                   f'Готовы продолжить и выбрать верный перевод английского слова?'
            keyboard = InlineKeyboards.learn_words_continue('Погнали 🏃')
            await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=keyboard)
            return
        elif today_words_str_state == 2:
            text = f'Достигнут лимит в изучении слов 🙈\n' \
                   f'Возвращайтесь завтра 🕑'
            await bot.send_message(chat_id=message.from_user.id, text=text)
            return

        user_level = user.level_english_user
        user_words_count_learn = user.words_count_learn
        user_words_dict = {'A1': user.A1_words,
                           'A2': user.A2_words,
                           'B1': user.B1_words,
                           'B2': user.B2_words,
                           'C': user.C_words}
        user_words = user_words_dict[user_level]
        # Словарь для заполнения новых слов для изучения
        current_words_to_learn = {'current': []}
        for lst in user_words.values():
            if len(current_words_to_learn['current']) == user_words_count_learn:
                break
            if lst[4] == 3:
                current_words_to_learn['current'].append(lst)
        if len(current_words_to_learn['current']) < user_words_count_learn:
            sorted_words = sorted(user_words.values(), key=lambda a: random.random())
            for lst in sorted_words:
                if len(current_words_to_learn['current']) == user_words_count_learn:
                    break
                if lst[4] == 0:
                    current_words_to_learn['current'].append(lst)

        # Если новых слов для изучения нет, предлагаем выбрать другой уровень английского
        if not len(current_words_to_learn['current']):
            text = f'Вы успешно изучили все слова текущего уровня\n' \
                   f'Выберите другой через меню!'
            await bot.send_message(chat_id=message.from_user.id, text=text)
            return

        # Словарь для дальнейшей проверки новых изученных слов
        current_words_to_learn_check = {'current_check': []}
        for lst in user_words.values():
            current_words_to_learn_check['current_check'].append(lst[2])

        # Запись списка слов для изучения в PostgreSQL
        user.current_words_to_learn = current_words_to_learn
        # Запись списка слов для дальнейшей проверки
        user.current_words_to_learn_check = current_words_to_learn_check
        session.commit()

        text = f'Вы получите слова для запоминания!\n' \
               f'Жмите > <b>Учить</b>'

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        one = types.InlineKeyboardButton(text='Учить',
                                         callback_data='learn')
        keyboard.add(one)
        await bot.send_message(chat_id=message.from_user.id, text=text, parse_mode='html', reply_markup=keyboard)

    elif message.text == 'Изменить анкету 📝':
        text, keyboard = InlineKeyboards.change_form()
        await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=keyboard)

    elif message.text == 'Таблица рейтинга 📊':
        users = session.query(User).order_by(User.score_table_rating.desc()).all()
        user = session.query(User).filter_by(id_telegram=message.from_user.id).first()
        is_current_user = user.user_name
        first_pg = 1
        second_pg = 2
        text, keyboard = InlineKeyboards.table_rating_output(first_pg=first_pg,
                                                             second_pg=second_pg,
                                                             is_current_user=is_current_user,
                                                             users=users)
        # Далее отправка сообщения
        await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=keyboard)

    elif message.text == 'Полная версия 💹':
        # Совершение оплаты пользователем

        # prices
        PRICE = types.LabeledPrice(label='Подписка на Бот', amount=399 * 100)

        # buy
        if config['payments_token'].split(':')[1] == 'TEST':
            text = 'Тестовый платеж'
            await bot.send_message(chat_id=message.from_user.id, text=text)

        await bot.send_invoice(chat_id=message.from_user.id,
                               title='Подписка на Бот',
                               description='Активация пожизненной подписки на Бот',
                               provider_token=config['payments_token'],
                               currency='rub',
                               photo_url='https://i.pinimg.com/736x/51/9e/53/519e53f3f72ba21337f84a9967f572cb.jpg',
                               photo_width=416,
                               photo_height=234,
                               photo_size=416,
                               is_flexible=False,
                               prices=[PRICE],
                               start_parameter='life_subscription',
                               payload='invoice_payload')

if __name__ == '__main__':
    # Создаем цикл loop и запускаем 2 задачи
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(check_subs_on_channel())

    # Запускаем сессию с БД PostgreSQL
    from DB import User
    from DB import get_session

    session = get_session()

    # Запуск Бота
    executor.start_polling(dp, skip_updates=False)
