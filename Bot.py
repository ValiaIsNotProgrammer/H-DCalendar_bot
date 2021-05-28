import re
import os
import time
import inspect

import telebot
from telebot import types
from threading import Thread
from datetime import datetime
from translate import Translator

from parser import get_holiday  # функция, парсиющая данные в зависимости от даты
from date_formating import regex_date  # функция, определяющая дату, форматируя ее

bot = telebot.TeleBot(os.environ['TELEGRAM_TOKEN'])

# язык бота
global LANGUAGE
LANGUAGE = 'Inglish'

# кнопки для навигации по боту
buttonsList = {
    "profile_key":
        {"Profile":
             ["My_dates", "Notifications",]},
    "settings_date_keu":
        {"Date settings":
             ['Set the current date', 'Change the date']},
    "language_key":
        {'Language':
             ['Русский', 'Inglish']},
    "search_key":
        {"Search":
             ['Search by current date', 'Search by the specified date']},
    "notificion_key":
        {"Notification":
            ['Disable Notification', 'Notification time']}
}  # многоключевой обьект dict
markup_finish_list = ["Back to menu", "Stop"]


def key_from_dict(value):
    key = str([x for x in value.keys()]).strip("['']")
    return key

# TODO: обработать переводчик, добавив альтернативный парсер или стороннию библиотеку
def translator(text):
    translator = Translator(to_lang="ru")
    return translator.translate(text) if LANGUAGE == 'Русский' else text



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


# TODO:
#  1) добавить кнопки для кастомизации напоминаний;
#  2) добавить кнопку возращения в InlineKeyboard;
#  3) добавить кнопку пользовательского ввода даты и надписи к ней;
#  4) изменить архитектуру запросов в более удобную и абстрактную

def makeKeyboard(text=None, past_request=None, message=None, finish=False):

    """
    Построение кастомной клавиатуры
    :param past_request: главный ключ словаря кнопок, в основном используется если > 1 ключа
    :param text: текст сообщения
    :param finish: определяет, включаеть завершающее меню или нет
    :return: InlineKeyBoard (встроенную в сообщение кастомную клавиатуру)
    """
    global LANGUAGE
    markup = types.InlineKeyboardMarkup()



    def animation_bar(message):
        # если функция вызвана не из "threading_load"(run), то исключение
        assert inspect.stack()[1][3] == "run"


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
                    return bot.delete_message(
                        chat_id=CHAT_ID,
                        message_id=message.message_id + 1
                    )
                bot.edit_message_text(chat_id=CHAT_ID,
                                      message_id=message.message_id + 1,
                                      text=clock)
                time.sleep(0.1)


    def threading_load(thread_func, main_func, **kwargs):

            global OVER
            OVER = None

            thread_args, main_args = [], {}
            for key in kwargs:
                if key == thread_func.__name__:
                    thread_args.append(kwargs[key])

            th = Thread(target=thread_func, args=thread_args)
            th.start()
            time.sleep(1)
            OVER = eval(main_func)
            th.join()


    def process_date_step(message):
        format_date = regex_date(message.text)
        bot.send_message(chat_id=CHAT_ID,
                         text=get_holiday(format_date)
                         )
        answer = "What\'s next?"
        bot.send_message(chat_id=CHAT_ID,
                         text=translator(answer),
                         reply_markup=makeKeyboard(finish=True),
                         parse_mode='HTML')



    if finish:
        def markup_finish():
            """
            Настройка заверщаюего меню
            :return: InlineKeyBoard (встроенную в сообщение кастомную клавиатуру)
            """
            for v in markup_finish_list:
                markup.add(types.InlineKeyboardButton(text=translator(v),
                                                      callback_data=v + '_button'))
            return markup

        if text == 'Back to menu_button':
            answer = "I\'m coming back..."
            # бот отправляет ответ-ожидание чтобы вернутся в главное меню
            bot.send_message(chat_id=CHAT_ID,
                             text=translator(answer))
            time.sleep(2)
            # бот удаляет ответ-ожидание и вместо него отправляет главное меню
            bot.delete_message(chat_id=CHAT_ID,
                               message_id=text.message_id + 1,  # т.к. message_id уже удаленно,
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


    # если опц. агрумента нет, то включается главное меню
    if (text in buttonsList.keys() or (not text) or text == "Back to menu_button"):
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



    markup.add(types.InlineKeyboardButton(text=translator('↩ Back ↩'),
                                          callback_data='back'))

    if text == 'Language':
        for v in buttonsList[past_request][text]:
            markup.add(types.InlineKeyboardButton(text=v,
                                                  callback_data=v + '_button'))
        return markup

    elif re.findall(('Русский_button|Inglish_button'), text):
        if text.split('_')[0] == "Русский":
            LANGUAGE = 'Русский'
        else:
            LANGUAGE = 'Inglish'

        kwargs = {"animation_bar": text}
        threading_load(animation_bar, "bot.send_message(chat_id=CHAT_ID, " \
                                      "text=translator('Language changed successfully'), " \
                                      "reply_markup=makeKeyboard())",
                       **kwargs)



    if text == 'Date settings':
        for v in buttonsList[past_request][text]:
            markup.add(types.InlineKeyboardButton(text=translator(v) if LANGUAGE == 'Русский' else v,
                                                  callback_data=v + '_button'))
        return markup

    elif text == 'Set the current date_button':
        # for v in buttonsList[orig_req][text]:
        #     markup.add(types.InlineKeyboardButton(text=v,
        #                                           callback_data=v + '_button'))
        year = '\a' + datetime.today().ctime().split()[-1]
        current_date = " ".join(language_date()) + year
        answer = "Today is {}. I couldn't set the date on your device. " \
                 "Either set the default date, or set your own".format(current_date)
        bot.send_message(chat_id=CHAT_ID,
                         text=answer)
        # return markup

    elif text == 'Change the date':
        pass



    if text == 'Search':
        for v in buttonsList[past_request][text]:
            markup.add(types.InlineKeyboardButton(text=translator(v) if LANGUAGE == 'Русский' else v,
                                                  callback_data=v + '_button'))
        return markup

    elif text == 'Search by current date_button':
        # answer = 'The request is being executed...'
        kwargs = {'animation_bar': message, "send_message":
                                            {'chat_id': CHAT_ID,
                                             'text': "translator(get_holiday(LANGUAGE)"}}
        threading_load(animation_bar, "bot.send_message(chat_id=CHAT_ID,"
                                      "                 text=get_holiday())",
                       **kwargs)

        answer = "What\'s next?"
        bot.send_message(chat_id=CHAT_ID,
                         text=translator(answer),
                         reply_markup=makeKeyboard(finish=True))

    elif text == 'Search by the specified date_button':
        answer = 'Enter the month and date in a format that is convenient for you'
        bot.send_message(chat_id=CHAT_ID,
                         text=translator(answer))
        bot.register_next_step_handler(text, process_date_step)





# TODO: добавление команд боту через BotFather
# главнное меню/вступительное окно навигации
@bot.message_handler(commands=['start'])
def handle_command_adminwindow(message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    answer = "Hi, again. This is the main menu where you can view your profile, " \
             "configure notifications, set the desired dates, " \
             "or simply use the date search to find out what holiday it is today"
    bot.send_message(chat_id=CHAT_ID,
                     text=translator(answer),
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
                                                       past_request=reply_markup_req,
                                                       message=message),
                             parse_mode='HTML')

        else:
            bot.send_message(chat_id=CHAT_ID,
                             text=keyboard_translator(answer),
                             reply_markup=makeKeyboard(text=reply_markup_text,
                                                       past_request=reply_markup_req,
                                                       message=message),
                             parse_mode='HTML')
    else:   # если ответ есть в листе завершающих кнопок, то включается завершающее меню
        makeKeyboard(text=reply_markup_text, message=message)


def get_back(call=None, back=False):
    global back_key
    if not back:
        data = call.data
        back_key = None
        for k1, v1 in buttonsList.items():
            if data in v1:
                back_key = k1
                break
            elif type(v1) == dict:
                for k2, v2 in v1.items():
                    if data in v2:
                        back_key = k2
                        break
        return back_key

    else:
        print('возращаюсь по ключю', back_key)
        answer = "What do you want to do now"
        bot.delete_message(chat_id=CHAT_ID,
                           message_id=call.message.id)
        return bot.send_message(text=translator(answer),
                                chat_id=CHAT_ID,
                                reply_markup=makeKeyboard(text=back_key))


# TODO: добавить корректную обработку всех callback'ов и кнопок навигации
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    try:
        if type(buttonsList[call.data]) == dict:
            answer = key_from_dict(buttonsList[call.data])
        else:
            answer = buttonsList[call.data]
    except KeyError:
            answer = call.data

    if call.data == 'back':
        get_back(call=call, back=True)

    else:
        bot.delete_message(chat_id=CHAT_ID,
                           message_id=call.message.message_id,
                           )
        handle_message_from_callback(call.message, reply_markup_text=answer,
                                     reply_markup_req=call.data)


def language_date():
    dt = datetime.today().ctime().split()[1:3]
    if LANGUAGE == 'Русский':
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
    return dt[1], dt[0]



while True:
    bot.polling()
    try:
        bot.polling(none_stop=True, interval=0, timeout=0)
    except:
        time.sleep(10)
