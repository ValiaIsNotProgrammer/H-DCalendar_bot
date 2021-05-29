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
from utilities import get_random_text

bot = telebot.TeleBot(os.environ['TELEGRAM_TOKEN'])

# язык бота
global LANGUAGE
LANGUAGE = 'Inglish'
# TODO: добавлять данные в базу данных (user_name, user_id, date, name)
USER_DATES = {"19 06": "Мое День Рождение", "25 01":  "Праздник 1", "01 01": "Новый Год"}

# кнопки для навигации по боту
buttonsList = {
    "profile_key":
        {"Profile":
             ["My dates", "Notifications",]},
    "settings_date_keu":
        {"Date settings":
             ['Set the current date', 'Change the date']},
    "language_key":
        {'Language':
             ['Русский', 'Inglish']},
    "search_key":
        {"Search":
             ['Search by current date', 'Search by the specified date']},
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

    def format_dictonary(dictonary):
        text = ""
        for id, (key, value) in enumerate(dictonary.items()):
            text += "{}. {} - {}\n" \
                .format(str(id + 1), ' '.join(regex_date(key).split('_')), value)
        return text


    if key == "Profile":
        answer = "Your profile information. " \
                 "Here you can view the notification settings and edit the date's"
        return translator(answer)

    elif key == "My dates_button":
        if USER_DATES:
            answer = "List of your dates:\n" \
                     "------------------------------------------\n{}" \
                     "-----------------------------------------\n" \
                     "You can add, edit, delete the dates you want by simply clicking " \
                     "on the corresponding button and specifying the date number."\
                      .format(format_dictonary(USER_DATES))
        else:
            answer = "You haven't added any of your dates yet"
        return translator(answer)

    elif (key == "Add first date!_button") or \
         (key == "Try again_add_button") or (key == "Add_button"):
            answer = "Enter the desired month and date " \
                     "in a format that is convenient for you"
            return translator(answer)

    elif key == 'Edit_button':
        answer = "Click on the date you want to edit"
        return translator(answer)

    elif (key.split('_')[0] in USER_DATES.keys()) and (key.split('_')[0]+"edit" == key):
        answer = "What do you want to change?"
        return translator(answer)

    elif key == 'Date_edit_button':
        answer = "Enter a new month and date value"
        return translator(answer)

    elif key == 'Name_edit_button':
        answer = "Enter a new name"
        return translator(answer)

    elif key == "Delete_button":
        answer = "Select the date you want to delete"
        return translator(answer)

    elif (key.split('_')[0] in USER_DATES.keys()) and (key.split('_')[0]+"_delete_button" == key):
        key = key.split("_")[0]
        answer = f"The name {USER_DATES[key]} with date " \
                 f"{' '.join(regex_date(key).split('_'))} was successfully deleted!"
        return translator(answer)


    elif key == "Notifications_button":
        answer = "Notification settings and data"
        return translator(answer)

    if key == 'Date settings':
        answer = 'Select the desired settings'
        return translator(answer)

    elif key == 'Language':
        answer = 'Select the desired language'
        return translator(answer)

    elif key == 'Search':
        answer = 'Choose a search method'
        return translator(answer)

    elif key == 'Search by current date_button':
        answer = "What\'s next?"
        return translator(answer)

    elif (key == 'Search by the specified date_button') or \
         (key == 'Try again_search_button'):
        answer = 'Enter the month and date in a format that is convenient for you'
        return translator(answer)

    elif key == "Back to menu_button":
        answer = "{}, what do you want this time?".\
            format(get_random_text("greeting"))
        return translator(answer)
    
    elif key == "Stop_button":
        answer = "Okay, if you need me, just write something, {}!".\
            format(get_random_text('farewell'))
        return translator(answer)
    else:
        return f'{keyboard_translator.__name__} --> ERROR VALUE: {key}'


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

    def process_date_step(message, finish=False, past_message=None):
        if (past_message == 'Search by the specified date_button') or \
           (past_message == "Add first date!_button"):
                global try_again_request
                try_again_request = past_message

        if finish:
            answer = "{}, what do you want now?".\
                format(get_random_text('greeting'))
            bot.send_message(text=translator(answer),
                             chat_id=CHAT_ID,
                             reply_markup=makeKeyboard())
        else:
            format_date = regex_date(message.text)
            bot.send_message(chat_id=CHAT_ID,
                             text=get_holiday(format_date)
                             )
            answer = "What\'s next?"
            bot.send_message(chat_id=CHAT_ID,
                             text=translator(answer),
                             reply_markup=makeKeyboard(text=try_again_request,
                                                       finish=True),
                             parse_mode='HTML')

    def adding_name(message, date=None, edit_name=False):
        input_name = message.text
        if edit_name:
            USER_DATES[OLD_KEY] = input_name
            answer = f'The name "{OLD_NAME}" was successfully changed to {input_name}!'
            return bot.send_message(text=translator(answer),
                                    chat_id=CHAT_ID,
                                    reply_markup=makeKeyboard(finish=True))

        USER_DATES[date] = input_name
        answer = "Date successfully added, what's next"
        return bot.send_message(text=translator(answer),
                                chat_id=CHAT_ID,
                                reply_markup=makeKeyboard(finish=True))

    def adding_dates(message, edit_date=False):
        input_date = regex_date(message.text)
        if type(input_date) == dict:
            process_date_step(message=message,
                            past_message=text)


        else:
            input_date = " ".join(input_date.split('_'))
            save_date = regex_date(input_date, savemod=True)
            if edit_date:
                USER_DATES[save_date] = USER_DATES.pop(OLD_KEY)
                answer = f"The value of {' '.join(regex_date(OLD_KEY).split('_'))} " \
                         f"was successfully renamed to {input_date}!"
                return bot.send_message(text=translator(answer),
                                        chat_id=CHAT_ID,
                                        reply_markup=makeKeyboard(finish=True))

            answer = "Great, now enter name " \
                     "of the holiday for {}".format(input_date)
            msg = bot.send_message(text=translator(answer),
                                   chat_id=CHAT_ID)
            args = [input_date]
            bot.register_next_step_handler(msg, adding_name, *args)






    if finish:
        for v in markup_finish_list:
            markup.add(types.InlineKeyboardButton(text=translator(v),
                                                  callback_data=v + '_button'))
        if text == "Search by the specified date_button":
            markup.add(types.InlineKeyboardButton(text=translator('Try again'),
                                                  callback_data='Try again_search_button'))
        elif text == "Add first date!_button":
            markup.add(types.InlineKeyboardButton(text=translator('Try again'),
                                                  callback_data='Try again_add_button'))

        return markup

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



    if text == "Profile":
        for v in buttonsList[past_request][text]:
            markup.add(types.InlineKeyboardButton(text=v,
                                                  callback_data=v + '_button'))
        return markup

    elif text == "My dates_button":
        if USER_DATES:
            custom_date_buttons = ['Add', 'Edit', 'Delete']
            for v in custom_date_buttons:
                markup.add(types.InlineKeyboardButton(text=translator(v),
                                                      callback_data=v+'_button'))
            return markup

        else:
            custom_date_buttons = ['Add first date!']
            for v in custom_date_buttons:
                markup.add(types.InlineKeyboardButton(text=translator(v),
                                                      callback_data=v+'_button'))
            return markup

    elif (text == "Add first date!_button") or \
         (text == 'Try again_add_button') or (text == "Add_button"):
            bot.register_next_step_handler(message, adding_dates)

    elif text == "Edit_button":
        for key in USER_DATES:
            markup.add(types.InlineKeyboardButton(text="{} - {}"\
                                                  .format(" ".join(regex_date(key).split("_")),
                                                          USER_DATES[key]),
                                                  callback_data=key+'_button'))
        return markup

    elif (text.split("_")[0] in USER_DATES.keys()) and ("edit" in text):
        key = text.split("_")[0]
        global OLD_KEY, OLD_NAME
        OLD_KEY, OLD_NAME = key, USER_DATES[key]
        edit_button_list = ['Date', 'Name']
        for v in edit_button_list:
            markup.add(types.InlineKeyboardButton(text=v,
                                                  callback_data=v + '_edit_button'))
        return markup

    elif text == 'Date_edit_button':
        args = [True]
        bot.register_next_step_handler(message, adding_dates, *args)

    elif text == "Name_edit_button":
        args = [True, OLD_KEY]
        return bot.register_next_step_handler(message, adding_name, *args)

    elif text == "Delete_button":
        for key in USER_DATES:
            markup.add(types.InlineKeyboardButton(text="{} - {}"\
                                                  .format(" ".join(regex_date(key).split("_")),
                                                          USER_DATES[key]),
                                                  callback_data=key+'_delete_button'))
        return markup

    elif (text.split("_")[0] in USER_DATES.keys()) and ("delete" in text):
        key = text.split("_")[0]
        del USER_DATES[key]
        return makeKeyboard(finish=True)



    elif text == "Notifications_button":
        pass



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
        kwargs = {'animation_bar': message, "send_message":
                                            {'chat_id': CHAT_ID,
                                             'text': "translator(get_holiday(LANGUAGE)"}}
        threading_load(animation_bar, "bot.send_message(chat_id=CHAT_ID,"
                                      "                 text=get_holiday())",
                       **kwargs)

        return makeKeyboard(finish=True)

    elif (text == 'Search by the specified date_button') or \
         (text == 'Try again_search_button'):
        args = [False, text]
        bot.register_next_step_handler(message, process_date_step, *args)



    if text == "Stop_button":
        args = [True]
        bot.register_next_step_handler(message, process_date_step, *args)







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
            past_request = call.data
            answer = key_from_dict(buttonsList[call.data])
        else:
            past_request = call.data
            answer = buttonsList[call.data]
    except KeyError:
            past_request = None
            answer = call.data

    if call.data == 'back':
        get_back(call=call, back=True)

    else:
        bot.delete_message(chat_id=CHAT_ID,
                           message_id=call.message.message_id,
                           )
        get_back(call=call)
        return bot.send_message(text=keyboard_translator(answer),
                                chat_id=CHAT_ID,
                                reply_markup=makeKeyboard(text=answer,
                                                          past_request=past_request,
                                                          message=call.message))


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
