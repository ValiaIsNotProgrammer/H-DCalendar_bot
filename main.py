from datetime import datetime
from collections import defaultdict
import re
import requests
from googletrans import Translator
from bs4 import BeautifulSoup
from date_formating import regex_date

def language_date(kakoy_prazdice=False, old_date=None):
    if not kakoy_prazdice:
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
        dt = old_date.split('_')[1]
        number = old_date.split('_')[0]
        if 'января' == dt:
            return "yanvar", number
        elif 'февраля' == dt:
            return "fevral", number
        elif 'марта' == dt:
            return "mart", number
        elif 'апреля' == dt:
            return "aprel", number
        elif 'мая' == dt:
            return "may", number
        elif 'июня' == dt:
            return "iyun", number
        elif 'июля' == dt:
            return "iyul", number
        elif 'августа' == dt:
            return "avgust", number
        elif 'сентября' == dt:
            return "sentyabr", number
        elif 'октября' == dt:
            return "oktyabr", number
        elif 'ноября' == dt:
            return "noyabr", number
        elif 'декабря' == dt:
            return "dekabr", number


def get_html(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
    }
    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        r.encoding = 'UTF-8'
        return r
    return 'Error, status: {}'.format(r.status_code)


def get_data(html, next_source=False):
    if next_source:
        soup = BeautifulSoup(html.text, 'lxml')
    else:
        soup = BeautifulSoup(html.text, 'lxml')
    if not next_source:
        if 'Википедия' in soup.text:
            return wikipedia(soup.find('div', class_='mw-parser-output'))
        else:
            return soup
    return kakoyprazdic(soup.find('div', class_='listing_wr'))


def kakoyprazdic(tag):
    divs = tag.find_all('div', itemprop="suggestedAnswer")  # основая часть найденных тегов
    divs.append(tag.find('div', itemprop="acceptedAnswer"))  # первый найденный запрос,
    # обычно в единственном экземпляре
    text = str()
    regex = "\(.*\)"
    for div in divs:
        text += re.sub(regex, "", div.text) + '\n'

    return text


def wikipedia(tag):
    holidays_dict = defaultdict(dict)
    for id_, g in enumerate(tag):
        try:
            h3 = g.find_next_sibling('h3')  # основной тег
            h3_sub = re.sub('(\n|\xa0)', '', h3.text.split('[')[0])  # очищаем тег от enter и пробелов между тире
            # в итоге получаем главный ключ/заголовок
            h4 = g.find_next_sibling('h4')  # опциональный ключ/заголовок, который иногда появляется
            dl = h3.find_next_sibling('dl')
            ul = h3.find_next_siblings('ul')[0]

            if h3.text == dl.find_previous_sibling().text:
                second_key = dl.text.split('—')[0].strip()
                holidays_dict[h3_sub][second_key] = '\n'.join(dl.text.replace('\xa0', '').split('\n')[1:])
                dl_next = dl.find_next_sibling()
                if dl_next.name == dl.name:
                    second_key = dl_next.text.split('\n')[0].strip()
                    holidays_dict[h3_sub][second_key] = "\n".join(dl_next.text.split('\n')[1:])

            if ul.find_all('li'):
                for l in ul.find_all('li'):
                    if len(ul.find_all('li')) > 1:  # если в теги ul больше одного тега li,
                        # то есть сделать перечисление через ":"
                        if l.find('ul'):  # если ul(значения после ":")
                            try:
                                head_word = l.text.split(':')[0]
                                holidays_dict[h3_sub][head_word] = l.find('ul').text
                            except TypeError:
                                pass

                        else:  # если в ключе только одно значение
                            try:
                                splt_tag = l.text.split('\xa0—')
                                holidays_dict[h3_sub][splt_tag[0]] = splt_tag[1]
                            except IndexError:
                                pass
                    else:
                        holidays_dict[h3_sub] = l.text

            if g.next.text == h4.text:
                old_tag = h4.find_previous_sibling('h3').text.split('[')[0]
                ul = h4.find_next_siblings('ul')[0]
                h4 = h4.text.split('[')[0]
                # пытаемся переписать существующий ключ
                try:
                    holidays_dict[old_tag][h4] = ul.text
                except TypeError:
                    # удаляем существующий ключ чтобы перезаписать его
                    del holidays_dict[old_tag]
                    holidays_dict[old_tag][h4] = ul.text




        except AttributeError:
            pass

    if not holidays_dict:
        dt = language_date(kakoy_prazdice=True, old_date=CURRENT_DATE)
        return get_data(get_html("https://kakoysegodnyaprazdnik.ru/baza/{}/{}".format(dt[0],
                                                                               dt[1])),
                 next_source=True)

    return construct_dict(delete_centure(holidays_dict))


def delete_centure(dictonary):
    excess_keys = set()
    for key_1, key_2 in dictonary.items():
        if type(key_2) == dict:
            for key in key_2.keys():
                try:
                    if int(key):
                        excess_keys.add(key_1)
                        break
                except ValueError:
                    pass
        elif re.findall('(XI|IX|XX)', key_1):
            excess_keys.add(key_1)

    for key in excess_keys:
        del dictonary[key]

    return dictonary


def get_emoji(text):
    tranlator = Translator()
    en_text = tranlator.translate(text).text.lower()

    if re.findall('(international|международные)', en_text):
        return "🌍"

    elif re.findall('(national|национальные)', en_text):
        return "🇺🇳"

    elif re.findall('(religious|религиозные)', en_text):
        return "✝️"

    else:
        return ' '


def construct_dict(dictonary):
    final_text = ""
    ge = get_emoji
    for key_1, key_2 in dictonary.items():
        if type(key_2) == dict:
            final_text = final_text + ge(key_1) + key_1.strip().upper() + ':\n'
            for key in key_2.keys():
                if len(key_2[key].split('\n')) > 1:
                    final_text = final_text + key + ':\n   ' + "\n   ".join(key_2[key].split('\n')) + '\n'
                else:
                    final_text = final_text + key + ' - ' + key_2[key] + '\n'
                    if len(key_2) <= 1:
                        dt = language_date(kakoy_prazdice=True, old_date=CURRENT_DATE)
                        return get_data(get_html("https://kakoysegodnyaprazdnik.ru/baza/{}/{}".format(dt[0],
                                                                                                      dt[1])),
                                        next_source=True)

        else:
            final_text = final_text + ge(key_1) + key_1.upper() + ' - ' + dictonary[key_1] + '\n'

    return re.sub("(\(.*\))|(\[.*\])|(\.|;)", '', final_text)


def get_holidays(lang, date=None):
    url = "https://ru.wikipedia.org/wiki/{}"
    global CURRENT_DATE
    if type(date) == dict:
        return date['error']
    elif date:
        CURRENT_DATE = date
    else:
        CURRENT_DATE = "_".join(language_date())
    translator = Translator()
    holidays_text = get_data(get_html(url.format(CURRENT_DATE)))
    if re.findall('(en|Inglish|inglish)', lang):
        holidays_text = translator.translate(holidays_text).text
        return holidays_text
    else:
        return holidays_text


# print(get_holidays(lang='ru',date="1_мая"))