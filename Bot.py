import re
import os
import time
import inspect
from datetime import datetime, timedelta

import telebot
from telebot import types
from threading import Thread
from googletrans import Translator

from parser import get_holiday  # функция, парсиющая данные в зависимости от даты
from date_formating import regex_date  # функция, определяющая дату, форматируя ее в нужный для парсера формат
from utilities import get_random_text  # функция, возращаюшая случайное значение из наборов выбранных наборов паттернов
from database import insert_into, get_user_data, is_query_username_bd  # функции для взаимодействия с базой данных

bot = telebot.TeleBot(os.environ['TELEGRAM_TOKEN'])

# TODO: настроить глобальные переменные во всех функциях
global LANGUAGE, CHAT_ID
LANGUAGE, CHAT_ID,  = 'Inglish', 0
USER_DATES = {}
# кнопки для навигации по боту
# TODO:
#  1) добавить все кнопки в buttonsList, для правильного функционирования кнопки back;
#  2) добавить возможность для добавления одноразовых событий, которые удаляются сразу после дня события
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


# TODO: превратить эту функцию в lambda, сделать более короче, проверить где она используется и заменить
def key_from_dict(value):
    key = str([x for x in value.keys()]).strip("['']")
    return key

def updater():
    global NOTIFICATION_TIME, BEFORE_DAY_VALUE
    NOTIFICATION_TIME, BEFORE_DAY_VALUE = "10", 1
    DEFAULT_DATA_USER = {"user_id": CHAT_ID,
                     "user_dates_name": ", ".join(list(USER_DATES.values())),
                     "user_dates_date": ", ".join(list(USER_DATES.keys())),
                     "notification_time": NOTIFICATION_TIME, "before_day_value": BEFORE_DAY_VALUE,
                     'language': LANGUAGE}
    while True:
        global USER_DATA
        USER_DATA = {"user_id": CHAT_ID,
                     "user_dates_name": ", ".join(list(USER_DATES.values())),
                     "user_dates_date": ", ".join(list(USER_DATES.keys())),
                     "notification_time": NOTIFICATION_TIME, "before_day_value": BEFORE_DAY_VALUE,
                     'language': LANGUAGE}
        if (str(DEFAULT_DATA_USER) != str(USER_DATA)):
            insert_into(USER_DATA)
            DEFAULT_DATA_USER = USER_DATA
        hour_now = datetime.today().strftime('%H')
        date_today = datetime.today().strftime("%d %m")
        before_count_days = (datetime.today() + timedelta(days=BEFORE_DAY_VALUE)).strftime("%d %m")
        time.sleep(3)
        for tm in USER_DATES:
            if (tm == date_today) or (before_count_days == tm):
                if hour_now == NOTIFICATION_TIME:
                    answer = 'Hi, I want to remind you that today is "{}"'.format(USER_DATES)
                    bot.send_message(chat_id=CHAT_ID,
                                     text=translator(answer))

# TODO: обработать переводчик, добавив альтернативный парсер или стороннию библиотеку
def translator(text):
    transltr = Translator()
    return transltr.translate(text, dest='ru').text if LANGUAGE == 'Русский' else text

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

    elif (key.split('_')[0] in USER_DATES.keys()) and (key.split('_')[0]+"_button" == key):
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


    if key == "Notifications_button":
        answer = "Notification settings. " \
                 "Now notifications are set at {} o'clock, " \
                 "for the day and on the day of the event".format(NOTIFICATION_TIME)
        return translator(answer)

    elif (key == "Early notifications_button") or (key == "Try again_notif_days_button"):
        answer = "Specify how many days to notify before the event"
        return translator(answer)

    elif (key == "Notification time_button") or (key == 'Try again_notification_button'):
        answer = "Specify the time in hours " \
                 "when you want to receive event notifications"
        return translator(answer)



    if key == 'Date settings':
        answer = 'Select the desired settings'
        return translator(answer)



    if key == 'Language':
        answer = 'Select the desired language'
        return translator(answer)

    elif re.findall(('Русский_button|Inglish_button'), key):
        answer = '{}, what you want now?'.format(get_random_text('greeting'))
        return translator(answer)




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

def change_in_old_data(old_data):
    print("До\n",USER_DATA)
    # TODO: сделать проверку дупликатов у USER_DATA при добавлении дат
    #  ибо при обновлении в updater USER_DATA может скопировать даты еще и с обновленного словаря дат
    for k, old_v in zip(USER_DATA, old_data):
        USER_DATA[k] = old_v
    dates = old_data[3].split(',')
    holiday = old_data[2].split(',')
    for dt, nm in zip(dates, holiday):
        if dt and nm:
            USER_DATES[dt.strip()] = nm.strip()
        else:
            USER_DATES[dt.strip()] = nm.strip()
            USER_DATES.pop(dt)
    print("После\n",USER_DATA)



# TODO:
#  1) добавить кнопку пользовательского ввода даты и надписи к ней;
#  2) сделать более удобную для review архитектуру, благодаря проверке past_request;
#  3) исправить переход кпопки language и анимации;
#  4) добавить везде перевод при создании клавиатуры
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
           (past_message == "Add first date!_button") or \
           (past_message == "Notification time_button") or \
           (past_message == "Early notifications_button"):
                global try_again_request
                try_again_request = past_message

        if finish:
            answer = "{}, what do you want now?".\
                format(get_random_text('greeting'))
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
            args = [save_date]
            bot.register_next_step_handler(msg, adding_name, *args)

    def change_notification(message, edit_days=False, edit_time=False):
        if edit_time:
            user_notification_time = message.text
            if user_notification_time.isdigit():
                if int(user_notification_time) <= 24:
                    if len([w for w in user_notification_time]) <= 2:
                        if len([w for w in user_notification_time]) == 1:
                            user_notification_time = "0" + user_notification_time
                        global NOTIFICATION_TIME
                        NOTIFICATION_TIME = user_notification_time
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
                    global BEFORE_DAY_VALUE
                    BEFORE_DAY_VALUE = int(user_notification_days)
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
            # pass
            bot.register_next_step_handler(message, adding_dates)

    elif text == "Edit_button":
        for key in USER_DATES:
            markup.add(types.InlineKeyboardButton(text="{} - {}"\
                                                  .format(" ".join(regex_date(key).split("_")),
                                                          USER_DATES[key]),
                                                  callback_data=key+'_button'))
        return markup

    elif (text.split("_")[0] in USER_DATES.keys()) and (text.split('_')[0]+"_button" == text):
        key = text.split("_")[0]
        global OLD_KEY, OLD_NAME
        OLD_KEY, OLD_NAME = key, USER_DATES[key]
        edit_buttons = ['Date', 'Name']
        for v in edit_buttons:
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



    if text == "Notifications_button":
        notification_buttons = ['Notification time',
                                'Early notifications']
        for v in notification_buttons:
            markup.add(types.InlineKeyboardButton(text=v,
                                                  callback_data=v + '_button'))
        return markup

    elif (text == "Notification time_button") or (text =='Try again_notification_button'):
        args = [False, True]
        bot.register_next_step_handler(message, change_notification, *args)

    elif (text == "Early notifications_button") or (text == "Try again_notif_days_button"):
        args = [True, False]
        bot.register_next_step_handler(message, change_notification, *args)






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

        kwargs = {"animation_bar": message}
        threading_load(animation_bar, "bot.send_message(chat_id=CHAT_ID, " \
                                      "text=translator('Language changed successfully'))",
                       **kwargs)

        return makeKeyboard()


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



@bot.message_handler(commands=['start'])
def handle_command_adminwindow(message):
    global CHAT_ID
    CHAT_ID = message.chat.id
    if is_query_username_bd(CHAT_ID):
        print(f"ПОЛЬЗОВАТЕЛЬ C ID {CHAT_ID} УЖЕ ЕСТЬ В БАЗЕ ДАННЫХ")
        change_in_old_data(get_user_data(CHAT_ID))

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
        answer = "{}, what do you want to do now".format(get_random_text('greeting'))
        bot.delete_message(chat_id=CHAT_ID,
                           message_id=call.message.id)
        return bot.send_message(text=translator(answer),
                                chat_id=CHAT_ID,
                                reply_markup=makeKeyboard(text=back_key))


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


NOTIFICATION_TIMER = Thread(target=updater)
NOTIFICATION_TIMER.start()
while True:
    bot.polling()
    try:
        bot.polling(none_stop=True, interval=0, timeout=0)
    except:
        time.sleep(10)
