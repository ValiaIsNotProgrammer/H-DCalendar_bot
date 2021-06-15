import re
import os
import time
import copy
import inspect
import log_app
import itertools
from datetime import datetime, timedelta

import telebot
import threading
from telebot import types
from threading import Thread
from googletrans import Translator

from parser import get_holiday  # функция, парсиющая данные в зависимости от даты
from date_formating import regex_date  # функция, определяющая дату, форматируя ее в нужный для парсера формат
from utilities import get_random_text  # функция, возращаюшая случайное значение из наборов выбранных наборов паттернов
from database import insert_into, get_user_data, is_query_username_bd  # функции для взаимодействия с базой данных
# TODO: 1) настроить язык - добавить просто готовый перевод;
#       2) настроить логи;
#       3) определиться с кнопками date settings;
#       4) настроить date_formatting на падежи месяцев, перевод месяцов,

logger = log_app.get_logger(__name__)



bot = telebot.TeleBot(os.environ['TELEGRAM_TOKEN'])

# TODO: настроить глобальные переменные во всех функциях
USER_DATA = {"user_id": 0,  # primary_key
             "user_dates_date": [],
             "user_dates_name": [],
             "notification_time": "10",
             "before_day_value": 1,
             'language': "English",
             'remember_later': 1}

# кнопки для навигации по боту
# TODO:
#  1) добавить все кнопки в buttonsList, для правильного функционирования кнопки back;
buttonsList = {
    "profile_key":
        {"Profile":
             ["My dates", "Notifications",]},
    "settings_date_keu":
        {"Date settings":
             ['Set the current date', 'Change the date']},
    "language_key":
        {'Language':
             ['Русский', 'English']},
    "search_key":
        {"Search":
             ['Search by current date', 'Search by the specified date']},
}  # многоключевой обьект dict

markup_finish_list = ["Back to menu", "Stop"]


def updater(TEST=True):

    def get_thread_notification(answer):
        def waiter():
            print('Отчет пошел на', 3600 * USER_DATA['remember_later'])
            time.sleep(3600 * USER_DATA['remember_later'])
            print('Отчет окончен')

        bot.send_message(chat_id=CHAT_ID,
                         text=translator(answer))
                         # reply_markup=makeKeyboard(text='Remember'))


        th = Thread(target=waiter, name='WaitThread')
        th.start()

    def insert_new_data(default_dict, new_dict):
        if (str(default_dict) != str(new_dict)):
            #  запись словаря без последнего значения
            insert_into(dict(itertools.islice(new_dict.items(), len(new_dict)-1)))
            return copy.deepcopy(new_dict)
        return default_dict


    DEFAULT_DATA_USER = {"user_id": 0,
                         "user_dates_date": [],
                         "user_dates_name": [],
                         "notification_time": "10",
                         "before_day_value": 1,
                         'language': "English"}
    while True:
        DEFAULT_DATA_USER = insert_new_data(DEFAULT_DATA_USER, USER_DATA)
        if TEST:
            date_today = "19 06"
            before_count_days = "18 06"
        hour_now = datetime.today().strftime('%H')
        # date_today = datetime.today().strftime("%d %m")
        # before_count_days = (datetime.today() - timedelta(days=USER_DATA["before_day_value"])).strftime("%d %m")
        time.sleep(5)
        delete_date, delete_name = None, None
        for tm, name in zip(USER_DATA["user_dates_date"], USER_DATA["user_dates_name"]):
            is_wait_thread = [True for thread in threading.enumerate() if 'WaitThread' == thread.name]
            if tm == date_today:
                # TODO: добавить функцию remember_later, которая будет после уведомления возращать
                #  кастомную клавиатуру с выбором "remember later" & "ok"
                if hour_now == USER_DATA["notification_time"] and not is_wait_thread:
                    answer = 'Hi, I want to remind you that today is "{}"'.format(name)
                    if "(one-time)" in name:
                        delete_date = tm
                        delete_name = name
                        break
                        # TODO: добавить асинхронную функцию записи значений, чтобы не ждать 1 час
                    get_thread_notification(answer)
                    break
            elif before_count_days == tm:
                if hour_now == USER_DATA["notification_time"] and not is_wait_thread:
                    answer = 'Hi, I want to remind you that tomorrow is "{}"'.format(name)
                    get_thread_notification(answer)
        if (delete_date and delete_name) and not is_wait_thread:
            del USER_DATA["user_dates_date"][USER_DATA["user_dates_date"].index(delete_date)]
            del USER_DATA["user_dates_name"][USER_DATA["user_dates_name"].index(delete_name)]
            get_thread_notification(answer)

# TODO: обработать переводчик, добавив альтернативный парсер или стороннию библиотеку
def translator(text) -> str:
    transltr = Translator()
    return transltr.translate(text, dest='ru').text if USER_DATA['language'] == 'Русский' else text

def keyboard_translator(key) -> str:
    """
    Функция опредялет текст сообщения в зависимости от ключей buttonList
    и язык в зависимости от переменной LANGUAGE
    :param key: сам ключ
    :return:
    """

    def format_lists(dates: list, names: list):
        text = ""
        for Id, (date, name) in enumerate(zip(dates, names)):
            text += "{}. {} - {}\n" \
                .format(str(Id + 1), ' '.join(regex_date(date).split('_')), name)
        return text

    #################################################################################################
    if key == "Profile":
        answer = "Your profile information. " \
                 "Here you can view the notification settings and edit the date's"
        return translator(answer)

    elif key == "My dates_button":
        if (USER_DATA["user_dates_date"] or USER_DATA["user_dates_name"]):
            answer = "List of your dates:\n" \
                     "------------------------------------------\n{}" \
                     "-----------------------------------------\n" \
                     "You can add, edit, delete the dates you want by simply clicking " \
                     "on the corresponding button and specifying the date number."\
                      .format(format_lists(USER_DATA["user_dates_date"],
                                            USER_DATA["user_dates_name"]))
        else:
            answer = "You haven't added any of your dates yet"
        return translator(answer)

    elif (key == "Add first date!_button") or (key == "Add_button"):
        answer = "Do you want to add a one-time or permanent event?"
        return translator(answer)

    elif (key == 'Permanent event_button') or (key == 'Try again_add_button') \
            or (key == 'One-time event_button'):
            answer = "Enter the desired month and date " \
                     "in a format that is convenient for you"
            return translator(answer)

    elif key == 'Edit_button':
        answer = "Click on the date you want to edit"
        return translator(answer)

    elif "_change_edit_button" in key:
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

    elif "_delete_button" in key:
        answer = f"The date was successfully deleted!"
        return translator(answer)

#################################################################################################
    if key == "Notifications_button":
        answer = "Notification settings. " \
                 "Now notifications are set at {} o'clock, " \
                 "for the day and on the day of the event".format(USER_DATA["notification_time"])
        return translator(answer)

    elif (key == "Early notifications_button") or (key == "Try again_notif_days_button"):
        answer = "Specify how many days to notify before the event"
        return translator(answer)

    elif (key == "Notification time_button") or (key == 'Try again_notification_button'):
        answer = "Specify the time in hours " \
                 "when you want to receive event notifications"
        return translator(answer)

#################################################################################################
    if key == 'Date settings':
        answer = 'Select the desired settings'
        return translator(answer)

#################################################################################################
    if key == 'Language':
        answer = 'Select the desired language'
        return translator(answer)

    elif re.findall(('Русский_button|English_button'), key):
        if key.split('_')[0] == "Русский":
            USER_DATA['language'] = 'Русский'
        else:
            USER_DATA['language'] = 'Inglish'
        answer = '{}, what you want now?'.format(get_random_text('greeting', USER_DATA['language']))
        return translator(answer)

#################################################################################################
    if key == 'Search':
        answer = 'Choose a search method'
        return translator(answer)

    elif key == 'Search by current date_button':
        answer = "What\'s next?"
        return translator(answer)

    elif (key == 'Search by the specified date_button') or \
         (key == 'Try again_search_button'):
        answer = 'Enter the month and date in a format that is convenient for you'
        return translator(answer)
#################################################################################################
    if key == "Remind me later_button":
        answer = "Okay, I'll remind you soon"
        return translator(answer)

    elif key == "OK_button":
        answer = "I hope you found the time for this"
        return translator(answer)

#################################################################################################
    if key == "Back to menu_button":
        answer = "{}, what do you want this time?".\
            format(get_random_text("greeting", USER_DATA['language']))
        return translator(answer)
    
    elif key == "Stop_button":
        answer = "Okay, if you need me, just write something, {}!".\
            format(get_random_text('farewell', USER_DATA['language']))
        return translator(answer)
    else:
        return f'{keyboard_translator.__name__} --> ERROR VALUE: {key}'

def change_in_old_data(old_data: tuple):
    last_data = tuple(USER_DATA.values())
    for k, old_v in zip(USER_DATA, old_data):
        if (k == "user_dates_date") or (k == "user_dates_name"):
            if k and old_v:
                USER_DATA[k] = list(map(str.strip, old_v.split(', ')))
        else:
            USER_DATA[k] = old_v
    logger.debug(f"The data \n\t{last_data}\n success changed to \n\t{old_data}")



# TODO:
#  1) добавить кнопку пользовательского ввода даты и надписи к ней;
#  2) сделать более удобную для review архитектуру, благодаря проверке past_request;
def makeKeyboard(text=None, past_request=None, message=None, finish=False):
    """
    Построение кастомной клавиатуры
    :param past_request: главный ключ словаря кнопок, в основном используется если > 1 ключа
    :param text: текст сообщения
    :param finish: определяет, включаеть завершающее меню или нет
    :return: InlineKeyBoard (встроенную в сообщение кастомную клавиатуру)
    """
    markup = types.InlineKeyboardMarkup()

    def animation_bar(message):
        # если функция вызвана не из "threading_load"(run), то исключение
        assert inspect.stack()[1][3] == "run"


        CLOCKS = ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕",
                  "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"]

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
           (past_message == "Add first date!_button") or \
           (past_message == "Notification time_button") or \
           (past_message == "Early notifications_button"):
                global try_again_request
                try_again_request = past_message

        if finish:
            answer = "{}, what do you want now?".\
                format(get_random_text('greeting', USER_DATA['language']))
            bot.send_message(text=translator(answer),
                             chat_id=CHAT_ID,
                             reply_markup=makeKeyboard())
        else:
            if try_again_request == 'Search by the specified date_button':
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

    def adding_name(message, one_time=False, edit_name=False):
        input_name = message.text
        if one_time:
            input_name = input_name + " " + translator(translator("(one-time)"))
        if edit_name:
            USER_DATA["user_dates_name"][USER_DATA["user_dates_name"].index(OLD_NAME)] = input_name
            answer = f'The name "{OLD_NAME}" was successfully changed to {input_name}!'
            return bot.send_message(text=translator(answer),
                                    chat_id=CHAT_ID,
                                    reply_markup=makeKeyboard(finish=True))

        USER_DATA["user_dates_name"].append(input_name)
        answer = "Date successfully added, what's next"
        return bot.send_message(text=translator(answer),
                                chat_id=CHAT_ID,
                                reply_markup=makeKeyboard(finish=True))

    def adding_dates(message, edit_date=False, one_time=False):
        input_date = regex_date(message.text)
        if type(input_date) == dict:
            bot.send_message(chat_id=CHAT_ID, text=translator(input_date['error']))
            process_date_step(message=message,
                            past_message=text)
        else:
            input_date = " ".join(input_date.split('_'))
            save_date = regex_date(input_date, savemod=True)
            if edit_date:
                indx = USER_DATA['user_dates_date'].index(OLD_DATE)
                USER_DATA["user_dates_date"][indx] = save_date
                answer = f"The value of {' '.join(regex_date(OLD_DATE).split('_'))} " \
                         f"was successfully renamed to {input_date}!"
                return bot.send_message(text=translator(answer),
                                        chat_id=CHAT_ID,
                                        reply_markup=makeKeyboard(finish=True))

            if one_time:
                kwargs = {"one_time": True}
            else:
                kwargs = {"one_time": False}
            USER_DATA['user_dates_date'].append(save_date)
            answer = "Great, now enter name " \
                     "of the holiday for {}".format(input_date)
            msg = bot.send_message(text=translator(answer),
                                   chat_id=CHAT_ID)
            bot.register_next_step_handler(msg, adding_name, **kwargs)

    def change_notification(message, edit_days=False, edit_time=False):
        if edit_time:
            user_notification_time = message.text
            if user_notification_time.isdigit():
                if int(user_notification_time) <= 24:
                    if len([w for w in user_notification_time]) <= 2:
                        if len([w for w in user_notification_time]) == 1:
                            user_notification_time = "0" + user_notification_time
                        USER_DATA["notification_time"] = user_notification_time
                        answer = f"Notification time successfully changed to " \
                                 f"{user_notification_time} o'clock"
                        return bot.send_message(text=translator(answer),
                                                chat_id=CHAT_ID,
                                                reply_markup=makeKeyboard(finish=True))
                    else:
                        answer = "Enter one to two digits"
                else:
                    answer = f"The value of hour {user_notification_time} is higher than the allowed value"
            else:
                answer = "The value must contain only numbers"
            bot.send_message(text=translator(answer),
                             chat_id=CHAT_ID)
            process_date_step(message=message,
                              past_message=text)
        if edit_days:
            user_notification_days = message.text
            if user_notification_days.isdigit():
                if [i for i in user_notification_days][0] != "0":
                    USER_DATA["before_day_value"] = int(user_notification_days)
                    answer = "The value was changed successfully. " \
                             f"Notifications will be sent {user_notification_days} days before the events " \
                             "and on the day of the events"
                    return bot.send_message(text=translator(answer),
                                            chat_id=CHAT_ID,
                                            reply_markup=makeKeyboard(finish=True))
                else:
                    answer = "The prefix must not be in the form of a zero"
            else:
                answer = "The value must contain only numbers"
            bot.send_message(text=translator(answer),
                             chat_id=CHAT_ID)
            process_date_step(message=message,
                              past_message=text)


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
        elif text == "Notification time_button":
            markup.add(types.InlineKeyboardButton(text=translator('Try again'),
                                                  callback_data='Try again_notification_button'))
        elif text == "Early notifications_button":
            markup.add(types.InlineKeyboardButton(text=translator('Try again'),
                                                  callback_data='Try again_notif_days_button'))


        return markup

    # если опц. агрумента нет, то включается главное меню
    if (text in buttonsList.keys() or (not text) or text == "Back to menu_button"):
        # итерация по кнопкам навигации, для надписей кнопок и их callback'ов
        for key, value in buttonsList.items():
            #  если значение ключа словарь, то берем только ключ
            if type(value) == dict:
                value_key = [k for k in value.keys()][0]
                markup.add(types.InlineKeyboardButton(text=translator(value_key),
                                                      callback_data=key))

            else:
                markup.add(types.InlineKeyboardButton(text=translator(value),
                                                      callback_data=key))
        return markup  # возращаем экземпляр InlineKeyboardMarkup()



    markup.add(types.InlineKeyboardButton(text=translator('↩ Back ↩'),
                                          callback_data='back'))


##################################################################################################
    if text == "Profile":
        for v in buttonsList[past_request][text]:
            markup.add(types.InlineKeyboardButton(text=translator(v),
                                                  callback_data=v + '_button'))
        return markup

    elif text == "My dates_button":
        if (USER_DATA["user_dates_date"] or USER_DATA["user_dates_name"]):
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

    elif (text == "Add first date!_button") or (text == "Add_button"):
        types_dates_buttons = ["One-time event", "Permanent event"]
        for v in types_dates_buttons:
            markup.add(types.InlineKeyboardButton(text=translator(v),
                                                  callback_data=v + '_button'))
        return markup

    elif text == "One-time event_button":
        kwargs = {"one_time": True}
        bot.register_next_step_handler(message, adding_dates, **kwargs)

    elif (text == 'Permanent event_button') or (text == 'Try again_add_button'):
        bot.register_next_step_handler(message, adding_dates)

    elif text == "Edit_button":
        for date, name in zip(USER_DATA["user_dates_date"], USER_DATA["user_dates_name"]):
            markup.add(types.InlineKeyboardButton(text="{} - {}"\
                                                  .format(" ".join(regex_date(date).split("_")),
                                                          name),
                                                  callback_data=f"{date}:{name}_change_edit_button"))
        return markup

    elif "_change_edit_button" in text:
        values = text.split("_")[0]
        name = values.split(":")[1]
        date = values.split(":")[0]

        global OLD_DATE, OLD_NAME
        OLD_DATE, OLD_NAME = date, name
        edit_buttons = ['Date', 'Name']
        for v in edit_buttons:
            markup.add(types.InlineKeyboardButton(text=v,
                                                  callback_data=v + '_edit_button'))
        return markup

    elif text == 'Date_edit_button':
        kwargs = {'edit_date': True}
        bot.register_next_step_handler(message, adding_dates, **kwargs)

    elif text == "Name_edit_button":
        kwargs = {"edit_name": True}
        if "one-time" in OLD_NAME:
            kwargs["one_time"] = True
        return bot.register_next_step_handler(message, adding_name, **kwargs)

    elif text == "Delete_button":
        for date, name in zip(USER_DATA["user_dates_date"], USER_DATA["user_dates_name"]):
            markup.add(types.InlineKeyboardButton(text="{} - {}" \
                                                  .format(" ".join(regex_date(date).split("_")),
                                                          name),
                                                  callback_data=f"{date}:{name}_delete_button"))
        return markup

    elif "_delete_button" in text:
        values = text.split("_")[0]
        name = values.split(":")[1]
        date = values.split(":")[0]
        del USER_DATA["user_dates_date"][USER_DATA['user_dates_date'].index(date)]
        del USER_DATA["user_dates_name"][USER_DATA['user_dates_name'].index(name)]
        return makeKeyboard(finish=True)
##################################################################################################
    if text == "Notifications_button":
        notification_buttons = ['Notification time',
                                'Early notifications']
        for v in notification_buttons:
            markup.add(types.InlineKeyboardButton(text=translator(v),
                                                  callback_data=v + '_button'))
        return markup

    elif (text == "Notification time_button") or (text =='Try again_notification_button'):
        kwargs = {"edit_time": True}
        bot.register_next_step_handler(message, change_notification, **kwargs)

    elif (text == "Early notifications_button") or (text == "Try again_notif_days_button"):
        kwargs = {"edit_days": True}
        bot.register_next_step_handler(message, change_notification, **kwargs)
##################################################################################################
    if text == 'Language':
        for v in buttonsList[past_request][text]:
            markup.add(types.InlineKeyboardButton(text=v,
                                                  callback_data=v + '_button'))
        return markup

    elif re.findall(('Русский_button|English_button'), text):

        kwargs = {"animation_bar": message}
        threading_load(animation_bar, "bot.send_message(chat_id=CHAT_ID, " \
                                      "text=translator('Language changed successfully'))",
                       **kwargs)

        return makeKeyboard()
##################################################################################################
    if text == 'Date settings':
        for v in buttonsList[past_request][text]:
            markup.add(types.InlineKeyboardButton(text=translator(v),
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
##################################################################################################
    if text == 'Search':
        for v in buttonsList[past_request][text]:
            markup.add(types.InlineKeyboardButton(text=translator(v),
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

    elif (text == 'Search by the specified date_button') or (text == 'Try again_search_button'):
        kwargs = {"past_message": text}
        bot.register_next_step_handler(message, process_date_step, **kwargs)
##################################################################################################
    # if text == 'Remember':
    #     remember_choice_buttons = ["Remind me later", "OK"]
    #     for v in remember_choice_buttons:
    #         markup.add(types.InlineKeyboardButton(text=translator(v),
    #                                               callback_data=v + '_button'))
    #     return markup
    #
    # elif text == "Remind me later_button":
    #     USER_DATA['remember_later'] = 1  # возращает кол-во часов, которое умножается на 3600 секунд
    #
    #
    # elif text == "OK":
    #     USER_DATA['remember_later'] = 24

##################################################################################################
    if text == "Stop_button":
        args = [True]
        bot.register_next_step_handler(message, process_date_step, *args)
##################################################################################################

@bot.message_handler(commands=['start'])
def handle_command_adminwindow(message: telebot.types.Message):
    logger.info(f"The user {message.chat.username} started the bot")

    global CHAT_ID
    CHAT_ID = message.chat.id
    USER_DATA['user_id'] = CHAT_ID
    start = False
    if is_query_username_bd(USER_DATA['user_id']):
        logger.info(f"The user {message.chat.username} in database")
        change_in_old_data(get_user_data(USER_DATA['user_id']))

    if not start:
        start = True
        notification_timer = Thread(target=updater, args=([True]))
        notification_timer.start()

    answer = "Welcome! This is the main menu where you can view your profile, " \
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
        logger.debug(f"UPDATE: new back key -> {back_key}")
        return back_key

    else:
        answer = "{}, what do you want to do now".format(get_random_text('greeting', USER_DATA['language']))
        bot.delete_message(chat_id=CHAT_ID,
                           message_id=call.message.id)
        return bot.send_message(text=translator(answer),
                                chat_id=CHAT_ID,
                                reply_markup=makeKeyboard(text=back_key))

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call: telebot.types.CallbackQuery):
    try:
        if type(buttonsList[call.data]) == dict:
            past_request = call.data
            answer = [k for k in buttonsList[call.data].keys()][0]
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
        # обновление ключа для возрата
        get_back(call=call)
        return bot.send_message(chat_id=CHAT_ID,
                                text=keyboard_translator(answer),
                                reply_markup=makeKeyboard(text=answer,
                                                          past_request=past_request,
                                                          message=call.message)
                                )

def language_date():
    dt = datetime.today().ctime().split()[1:3]
    if USER_DATA['language'] == 'Русский':
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
