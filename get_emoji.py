import re
import requests
from bs4 import BeautifulSoup
from translate import Translator
# from selenium import webdriver
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

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


if __name__ == '__main__':
    get_emoji('Змея')