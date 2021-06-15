import re
import random

from bs4 import BeautifulSoup


def get_emoji(text):


    def translator(text):
        translator = Translator(from_lang="ru", to_lang="en")
        return translator.translate(text)


    # def get_emoji_from_emojipedia(text):
    #     translated_text = translator(text)
    #     print(translated_text)
    #     url = "https://emojipedia.org/search/?q={}".format(translated_text)
    #     r = requests.get(url)
    #     soup = BeautifulSoup(r.text, 'lxml')
    #     tag = soup.find('ol', class_="search-results")
    #     result = tag.find('span', class_='emoji').text
    #     if result == "😞":
    #         return text
    #     return f"{result} {text}"



    if re.findall('(Международные)', text):
        return "🌍{}".format(text)

    elif re.findall('(Национальные)', text):
        return "🇺🇳{}".format(text)

    elif re.findall('(Религиозные)', text):
        return "✝️{}".format(text)

    elif re.findall('(Именины)', text):
        return "⚕️{}".format(text)

    else:
        return text
        # return get_emoji_from_emojipedia(text)


def get_random_text(part, lang):
    """
    Перебирает из определенных листов одну случайную фразу, которая зависит от part
    :list of parts: greeting, farewell, next,
    :param part: часть/структура сообщения, в которую нужно передавать разные значения
    :return: одну случайную фразу под определенную часть предложения
    """
    if part == 'greeting':
        if lang == "Русский":
            list_of_greeting = ['категорически приветствую', "эй, как дела", "и снова привет",
                                "доброго времени суток", "привет", "как поживаешь", "здравствуй",
                                "и снова здравствуй", "это снова я", "снова ты? Как дела", "рад что ты вернулся",
                                "алоха", "здравстуйте, сэр", "опять работа..",
                                ]
        else:
            list_of_greeting = ["categorically welcome", "hello", "welcome", "welcome back",
                                "good to see you again", "you again", "and again hello", "hey",
                                "how are you", "aloha", "how are you doing", "how are things going",
                                "how are you getting on", "howdy", "hiya", "g'day", "oh, you here",
                                "hello there",
                                ]
        return random.choice(list_of_greeting).capitalize()
    elif part == 'farewell':
        if lang == "Русский":
            list_of_farewell = ["прощайте", "пока", "до встречи", "увидимся", "до скорой встречи",
                                "до свидания", "до скорого", "хорошего дня", "всего доброго", "рад был вам помочь",
                                "всегда пожалуйства", "всегда пожалуйства, Ваш бездушный бот",
                                "удачи", "спокойного времени суток"]
        else:
            list_of_farewell = ["goodbye", "see you later", "bye", "all the best",
                                "see you soon", "aloha", "happy holidays", "good luck",
                                "have a nice day", "so I don't want to say goodbye",
                                'time to say "goodbye"', "aloha", "bye bye",]
        return random.choice(list_of_farewell)

if __name__ == '__main__':
    pass
