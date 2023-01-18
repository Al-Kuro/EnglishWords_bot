from aiogram import Bot, Dispatcher, executor, types
import asyncio
import logging
import json
import random

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


# Функция проверки на членство в канале (Исправить!!!) (Если вдруг пользователь решит отписаться от группы)
async def check_subs_on_channel():
    while True:
        all_users = session.query(User).filter(User.user_state == 0).all()
        if all_users:
            for user in all_users:
                res = await bot.get_chat_member(-1001653709784, user.id_telegram)
                if res.status in ['member', 'creator']:
                    await bot.delete_message(chat_id=user.id_telegram, message_id=user.start_msg)
                    text, keyboard = InlineKeyboards.fill_form_start()
                    await bot.send_message(chat_id=user.id_telegram, text=text, reply_markup=keyboard)

                    for usr in all_users:
                        usr.user_state = 1
                    session.commit()
        await asyncio.sleep(5)


# Обработчик команды '/start'
@dp.message_handler(commands=['start'])
async def send_welcome(message):
    is_user_exist = session.query(User).filter_by(id_telegram=message.from_user.id).first()
    if not is_user_exist:
        new_user = User(message.from_user.username, message.from_user.id)
        session.add(new_user)

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        one = types.InlineKeyboardButton(text='Подписаться',
                                         url='https://t.me/english_words_b',
                                         callback_data='hello')
        keyboard.add(one)

        text = 'Добро пожаловать!\nДля взаимодействия с Ботом подпишитесь на канал по ссылке ниже:'
        msg = await message.answer(text=text, reply_markup=keyboard)
        msg_id = msg.message_id
        new_user.start_msg = msg_id


# Обработчик инлайн анкетирования
@dp.callback_query_handler(lambda call: call.data in get_call_data_form()[1])
async def fill_form_call_logic(call):

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
async def learn_words_call_logic(call):
    print(session)
    user = session.query(User).filter_by(id_telegram=call.from_user.id).first()
    current_words_to_learn = user.current_words_to_learn

    is_exist = 0
    check_length = len(current_words_to_learn['current'])
    for lst in current_words_to_learn['current']:
        if lst[4] == 0:
            word = lst[0]
            transcription = lst[1]
            translation = lst[2]
            audio = lst[3]
            word_state = lst[4]
            text = f'<b>{word}</b>\n' \
                   f'{transcription}\n\n' \
                   f'{translation}'
            keyboard = InlineKeyboards.learn_words()
            await bot.send_voice(chat_id=call.from_user.id, voice=audio, caption=text, reply_markup=keyboard,
                                 parse_mode='html')
            lst[4] = 1
            user.current_words_to_learn = current_words_to_learn
            session.commit()
            #break
        else:
            is_exist += 1
            if is_exist == check_length:
                text = f'Слова закончились\n' \
                       f'Готовы проверить результат?'
                keyboard = InlineKeyboards.learn_words_end()
                await bot.send_message(chat_id=call.from_user.id, text=text, reply_markup=keyboard)


# Обработчик стартовой клавиатуры
@dp.message_handler(text=ReplyKeyboards.buttons_start)
async def hello(message):
    if message.text == 'Учить слова 📖':
        user = session.query(User).filter_by(id_telegram=message.from_user.id).first()
        user_level = user.level_english_user
        user_words_count_learn = user.words_count_learn
        user_words_dict = {'A1': user.A1_words,
                           'A2': user.A2_words,
                           'B1': user.B1_words,
                           'B2': user.B2_words,
                           'C1': user.C1_words}
        user_words = user_words_dict[user_level]
        current_words_to_learn = {'current': []}
        for lst in user_words.values():
            if len(current_words_to_learn['current']) == user_words_count_learn:
                break
            count = 0
            if lst[4] == 1:
                current_words_to_learn['current'].append(lst)
                count += 1
        if len(current_words_to_learn['current']) < 5:
            sorted_words = sorted(user_words.values(), key=lambda a: random.random())
            for lst in sorted_words:
                if len(current_words_to_learn['current']) == user_words_count_learn:
                    break
                if lst[4] == 0:
                    current_words_to_learn['current'].append(lst)

        # Запись списка слов для изучения в PostgreSQL
        user.current_words_to_learn = current_words_to_learn
        session.commit()

        text = f'Вы получите слова для запоминания!\n' \
               f'Жмите > <b>Учить</b>'

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        one = types.InlineKeyboardButton(text='Учить',
                                         callback_data='learn')
        keyboard.add(one)
        await bot.send_message(chat_id=message.from_user.id, text=text, parse_mode='html', reply_markup=keyboard)

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
    executor.start_polling(dp)
