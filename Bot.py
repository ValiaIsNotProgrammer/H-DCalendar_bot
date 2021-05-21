import telebot
import json
from telebot import types
import ast
from datetime import datetime
from threading import Thread
import asyncio
import re
import os
import time
from collections import defaultdict
from telebot import types
from googletrans import Translator
from main import get_holidays  # функция, парсиющая данные в зависимости от даты
from date_formating import regex_date  # функция, определяющая дату, форматируя ее

bot = telebot.TeleBot(os.environ['TELEGRAM_TOKEN'])

lkjaksldf
adfja;df
lkadjsfla;klf
# язык бота
global LANGUAGE
LANGUAGE = 'Inglish'
# кнопки для навигации по боту
buttonsList = defaultdict(str, {
    "correct_date_button": {"Date settings": ['Current date', 'Change the date']},
    "language_button": {'Language': ['Русский', 'Inglish']},
    "search_button": {"Search": ['Search by current date', 'Search by the specified date']},
})  # многоключевой обьект dict
markup_finish = ["Back to menu", "Stop"]

# возращает главный ключ по типу str
def key_from_dict(value):
    key = str([x for x in value.keys()]).strip("['']")
    return key


# переводчик, используемый в основном для текста сообщений
def translator(text):
    translator = lambda tx: Translator().translate(tx, dest='ru').text.strip("'[]'")
    return translator(text) if LANGUAGE == 'Русский' else text


# функция определяющая текст сообщения от основных кнопок
def keyboard_translator(key):
    """
    Функция опредялет текст сообщения в зависимости от ключей buttonList
    и язык в зависимости от переменной LANGUAGE
    :param key: сам ключ
    :return:
    """
    if key == 'Date settings':
        answer = 'Select the desired settings'
        return translator(answer)

    elif key == 'Language':
        answer = 'Select the desired language'
        return translator(answer)

    elif key == 'Search':
        answer = 'Choose a search method'
        return translator(answer)
    elif key == 'Search by current date':
        answer = "What\'s next?"
        return translator(answer)
    else:
        return None


# функция для создания кнопок навигации
def makeKeyboard(text=None, orig_req=None, message=None, finish=False):
    global LANGUAGE
    """
    Построение кастомной клавиатуры
    :param orig_req: главный ключ словаря кнопок, в основном используется если > 1 ключа
    :param message: сообщение с его характеристиками
    :param finish: определяет, включаеть завершающее меню или нет
    :return: InlineKeyBoard (встроенную в сообщение кастомную клавиатуру)
    """

    def animation_bar(message):
        CLOCKS = {
            "🕐": "One O’Clock", "🕑": "Two O’Clock", "🕒": "Three O’Clock",
            "🕓": "Four O’Clock", "🕔": "Five O’Clock", "🕕": "Six O’Clock",
            "🕖": "Seven O’Clock", "🕗": "Eight O’Clock", "🕘": "Nine O’Clock",
            "🕙": "Ten O’Clock", "🕚": "Eleven O’Clock", "🕛": "Twelve O’Clock",
        }

        bot.send_message(chat_id=CHAT_ID, text="🕛")
        while True:
            for clock in CLOCKS:
                if OVER:
                    print('whaaa?')
                    return bot.delete_message(
                        chat_id=CHAT_ID,
                        message_id=message.message_id + 1
                    )
                bot.edit_message_text(chat_id=CHAT_ID,
                                      message_id=message.message_id + 1,
                                      text=clock)
                time.sleep(0.1)


    def threading_load(thread, over):
        global OVER
        OVER = None
        for tp in (thread, over):
            assert type(tp) == tuple
            assert type(tp[1]) == dict
        thread_func = thread[0]
        over_func = over[0]
        over_args = dict()
        thread_args = []

        for key, value in over[1].items():
            if type(value) == dict:
                for k,v in value.items():
                    key_arg = key
                    over_args_func = (k,v)
            else:
                over_args[key] = value

        for value in thread[1].values():
            thread_args.append(value)
        thread_args = tuple(thread_args)


        print(over_func.__code__.co_varnames)
        th = Thread(target=thread_func,
                    args=(thread_args))

        th.start()
        OVER = over_func(chat_id=CHAT_ID, text=get_holidays(LANGUAGE)) # key_arg = over_args_func[0](over_args_func[1])

        th.join()




    markup = types.InlineKeyboardMarkup()

    # если опц. агрумента нет, то включается главное меню
    if (not text) and (not finish):
        # итерация по кнопкам навигации, для надписей кнопок и их callback'ов
        for key, value in buttonsList.items():
            #  если значение ключа словарь, то берем только ключ
            if type(value) == dict:
                value_key = key_from_dict(value)

                markup.add(types.InlineKeyboardButton(text=translator(value_key),
                                                      callback_data=key))
            else:
                markup.add(types.InlineKeyboardButton(text=translator(value),
                                                      callback_data=key))
        return markup  # возращаем экземпляр InlineKeyboardMarkup()


    elif finish:
        def markup_finish():
            """
            Настройка заверщаюего меню
            :return: InlineKeyBoard (встроенную в сообщение кастомную клавиатуру)
            """
            global markup_finish
            markup_finish = ["Back to menu", "Finish"]
            for v in markup_finish:
                markup.add(types.InlineKeyboardButton(text=translator(v) if LANGUAGE == 'Русский' else v,
                                                      callback_data=v + '_button'))
            return markup

        if text == 'Back to menu_button':
            print(text)
            answer = "I\'m coming back..."
            # бот отправляет ответ-ожидание чтобы вернутся в главное меню
            bot.send_message(chat_id=CHAT_ID,
                             text=translator(answer))
            time.sleep(2)
            # бот удаляет ответ-ожидание и вместо него отправляет главное меню
            bot.delete_message(chat_id=CHAT_ID,
                               message_id=message.message_id + 1,  # т.к. message_id уже удаленно,
                               # то нужно добавить к id значение, равно кол-ву сообщенией,
                               # отправленных после удаления
                               )
            # возврат в главное меню
            answer = "Choose the desired setting"
            bot.send_message(chat_id=CHAT_ID, text=answer,
                             reply_markup=makeKeyboard(),
                             parse_mode='HTML')

        elif text == 'Finish_button':
            answer = 'Just send any symbol or command so that I can contact you again!'

        else:
            return markup_finish()


    elif text == 'Language':
        for v in buttonsList[orig_req][text]:
            markup.add(types.InlineKeyboardButton(text=v,
                                                  callback_data=v + '_button'))
        return markup

    elif re.findall(('Русский_button|Inglish_button'), text):
        if text.split('_')[0] == "Русский":
            LANGUAGE = 'Русский'
        else:
            LANGUAGE = 'Inglish'
        answer = 'Change language...'
        animation_bar(message, translator(answer))
        answer = "Choose the desired setting"

        bot.delete_message(chat_id=CHAT_ID, message_id=message.message_id + 1)
        return bot.send_message(chat_id=CHAT_ID, text=translator(answer),
                                reply_markup=makeKeyboard())

    elif text == 'Date settings':
        for v in buttonsList[orig_req][text]:
            markup.add(types.InlineKeyboardButton(text=translator(v) if LANGUAGE == 'Русский' else v,
                                                  callback_data=v + '_button'))
        return markup

    elif text == 'Current date_button':
        year = '\a' + datetime.today().ctime().split()[-1]
        bot.send_message(chat_id=CHAT_ID,
                         text=" ".join(language_date()) + year if LANGUAGE == 'Русский' \
                             else " ".join(datetime.today().ctime().split()[1:3]) \
                                  + year,
                         parse_mode='HTML')

    elif text == 'Search':
        for v in buttonsList[orig_req][text]:
            markup.add(types.InlineKeyboardButton(text=translator(v) if LANGUAGE == 'Русский' else v,
                                                  callback_data=v + '_button'))
        return markup

    elif text == 'Search by current date_button':
        answer = 'The request is being executed...'
        # th = Thread(target=animation_bar, args=(translator(answer)))
        # th.start()
        # send_message = bot.send_message(chat_id=CHAT_ID,
        #                                 text=get_holidays(lang=LANGUAGE))
        # send_message
        # th.join()
        args_thread = {'message': message,}
        args_over = {'chat_id': CHAT_ID, 'text': {get_holidays : LANGUAGE}}
        # dump = json.load(args_over)
        # print(dump)
        threading_load(thread=(animation_bar, args_thread),
                       over=(bot.send_message, args_over)
                       )


        # bot.send_message(chat_id=CHAT_ID,
        #                  text=keyboard_translator(text.split('_')[0]),
        #                  reply_markup=makeKeyboard(finish=True),
        #                  parse_mode='HTML')


    elif text == 'Search by the specified date_button':
        answer = 'Enter the month and date in a format that is convenient for you'
        bot.send_message(chat_id=CHAT_ID,
                         text=translator(answer) if LANGUAGE == 'Русский' else answer)
        bot.register_next_step_handler(message, process_date_step)


def process_date_step(message):
    format_date = regex_date(message.text)
    bot.send_message(chat_id=CHAT_ID,
                     text=get_holidays(lang=LANGUAGE,
                                       date=format_date)
                     )
    answer = "What\'s next?"
    bot.send_message(chat_id=CHAT_ID,
                     text=translator(answer),
                     reply_markup=makeKeyboard(finish=True),
                     parse_mode='HTML')


# главнное меню/вступительное окно навигации
@bot.message_handler(commands=['start'])
def handle_command_adminwindow(message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    bot.send_message(chat_id=CHAT_ID,
                     text="Выбери нужную настройку" if LANGUAGE == 'Русский'
                     else "Choose the desired setting",
                     reply_markup=makeKeyboard(),
                     parse_mode='HTML')


# функция для ответа на нажатие кнопок навигации
@bot.message_handler()
def handle_message_from_callback(message, reply_markup_text=None, reply_markup_req=None):
    finish_trigger_list = [  # кнопки, после которых следует завершающее меню
        'Current date', 'Change the date','Русский',
        'Inglish','Search by current date', 'Search by the specified date'
    ]
    answer = reply_markup_text.split('_')[0]
    if answer not in finish_trigger_list:
        if keyboard_translator(reply_markup_text):
            bot.send_message(chat_id=CHAT_ID,
                             text=keyboard_translator(reply_markup_text),
                             reply_markup=makeKeyboard(text=reply_markup_text,
                                                       orig_req=reply_markup_req,
                                                       message=message),
                             parse_mode='HTML')

        else:
            bot.send_message(chat_id=CHAT_ID,
                             text=keyboard_translator(answer),
                             reply_markup=makeKeyboard(text=reply_markup_text,
                                                       orig_req=reply_markup_req,
                                                       message=message),
                             parse_mode='HTML')
    else:   # если ответ есть в листе завершающих кнопок, то включается завершающее меню
       makeKeyboard(text=reply_markup_text,
                    message=message)




# функция описывающая поведения ответа кнопок навигации
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if type(buttonsList[call.data]) == dict:
        answer = key_from_dict(buttonsList[call.data])
    else:
        if buttonsList[call.data]:
            answer = buttonsList[call.data]
        else:
            answer = call.data

    bot.delete_message(chat_id=CHAT_ID,
                       message_id=call.message.message_id,
                       )

    handle_message_from_callback(call.message, reply_markup_text=answer,
                                 reply_markup_req=call.data)


def language_date():
    # if lang == 'ru':
    dt = datetime.today().ctime().split()[1:3]
    if 'Jan' in dt:
        return dt[1], 'января'
    elif 'Feb' in dt:
        return dt[1], 'февраля'
    elif 'Mar' in dt:
        return dt[1], 'марта'
    elif 'Apr' in dt:
        return dt[1], 'апреля'
    elif 'May' in dt:
        return dt[1], 'мая'
    elif 'Jun' in dt:
        return dt[1], 'июня'
    elif 'Jul' in dt:
        return dt[1], 'июля'
    elif 'Aug' in dt:
        return dt[1], 'августа'
    elif 'Sep' in dt:
        return dt[1], 'сентября'
    elif 'Oct' in dt:
        return dt[1], 'октября'
    elif 'Nov' in dt:
        return dt[1], 'ноября'
    elif 'Dec' in dt:
        return dt[1], 'декабря'
    else:
        print('Uncorrect date')


while True:
    bot.polling()
    try:
        bot.polling(none_stop=True, interval=0, timeout=0)
    except:
        time.sleep(10)
