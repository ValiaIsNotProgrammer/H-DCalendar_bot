import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from date_formating import regex_date
from utilities import get_emoji


def get_html(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/85.0.4183.121 Safari/537.36'
    }
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        r.encoding = 'UTF-8'
        return r
    return 'Error, status: {}'.format(r.status_code)


def get_data(html):
    soup = BeautifulSoup(html.text, 'lxml')
    return wikipedia(soup)


def wikipedia(soup):
    """
    Парсит данные с wikipedia
    :param soup: обьект BeautifulSoap
    :return: возращает отформатированный текст со страницы
    """

    def get_head_values(next_iter_list):
        """
        Так как сайт не имеет определенной иерархии тэгов и их атрибутов,
        то функция итерируется по одноуровневым тэгам в глобальном списке тэгов по срезу [(Id+1),:]
        :param next_iter_list: обьект глобального листа тэгов
        :return: значения под нужный заголовок и форматирует их
        """

        head_values = []
        # текст и словарь для подзаголовков
        sub_head = ""
        sub_dict = {}

        for tag in next_iter_list:
            sub_regex = re.findall('<dl>|mw-headline|h4', str(tag))
            main_regex = re.findall('<ul>|<li/>', str(tag))

            if sub_regex:
                sub_head = tag.text
            elif sub_head:
                if main_regex:
                    sub_dict[sub_head] = tag.text
                    sub_head = None

            if main_regex:
                head_values.append(tag.text)
            elif tag.name == "h3":
                return get_format_text(head_values, sub_dict)

    def get_format_text(raw_row, sub_dict):
        """
        Итерируется по фильтрованной строке по условиям и форматирует ее
        :param raw_row: строка в тэге
        :param sub_dict: подсловарь, который дает быстрое и хорошее форматирование
        (является дополнительным, ибо он заполняется только в заголовке "Религиозные")
        :return: форматированную строку в тэге под заголовк
        """

        def iter_dict_v1(values_list, split_list, break_point_sep):
            """
            Для итерированию по обьекту str разделенным определенным разделителем
            :param values_list: главный, глобальный итерируемый обьект
            :param split_list: обьект, который разделили на определенный разделитель
            :param break_point_sep: точка останова
            :return: кортеж из форматированного текста и список пройденных значений,
            который нужен чтобы избежать повторений этих значений и сразу их пропустить
            """

            text = ""
            values_head = []  # список пройденных значений
            head_val = split_list[0].strip()
            origin_value = [v for v in values_list if head_val in v][0]
            Id = values_list.index(origin_value)  # получаем id, который начинает итерацию сразу после заголовка

            text += get_emoji(head_val) + ":\n\t  "
            try:
                for v in values_list[(Id + 1):]:
                    #  если доходим до строчки с точкой останова, то завершаем цикл
                    if len(v.split(break_point_sep)) > 1:
                        text = text[:-1]  # убираем два лишних пробела в конченой строке
                        break
                    values_head.append(v)
                    text += v + "\n\t  "
            except KeyError:
                return text, values_head
            return text, values_head

        def iter_dict_v2(sub_dict):
            """
            Для итерирования по настояющему словарю,
            который глобально представляет из себя подсловарь
            :param sub_dict: обьект подсловаря
            :return: форматированный текст
            """
            text = ""
            for k, v in sub_dict.items():
                # фильтруем подзаголовк и его значения от всех скобок
                head = get_emoji(re.sub("[(\[].*?[)\]]", '', k).strip())
                head_values = re.sub("[(\[].*?[)\]]", '', v).strip().split('\n')
                text += head + ":\n\t\t" + "\n\t\t".join(head_values)
                text += "\n\t"
            return text

        text = ""
        passed_values = []  # значения в тэгах, которые уже были
        # фильтруем сырую строку и для уверенности заменяем необычное тире на дефолтное
        raw = raw_row[0].replace(u'\xa0', u' ').strip().replace('—', '-')
        values = re.sub("[(\[].*?[)\]]", '', raw).split("\n")  # фильтруем от скобок и разделяем по новой строке

        for id, v in enumerate(values):
            # TODO: сделать обработку только для значений, исключая ключи
            #  (сделать проверку по кол-ву значений после ключа (разделителя))
            dash_splt_val = v.split('-')
            coln_splt_val = v.split(':')
            if v in passed_values:
                pass

            elif sub_dict:
                text += iter_dict_v2(sub_dict)
                return text

            else:
                if len(dash_splt_val) > 1:
                    head_1 = dash_splt_val[0].strip()
                    args = dash_splt_val[1].strip()
                    if len(head_1.split(',')) > 1:
                        head_2 = ", ".join(get_emoji(h) for h in head_1.split(',')).strip()
                        text += f"{head_2} - {args}\n\t"
                    else:
                        text += f"{get_emoji(head_1)} - {args}\n\t"

                elif len(coln_splt_val) > 1:
                    tx, vls = iter_dict_v1(values, coln_splt_val, "-")
                    text += tx.strip() + "\n\t"
                    [passed_values.append(v) for v in vls]

                else:
                    text += v.strip() + "\n\t"
        return text[:-1]

    holiday_text = ""
    # TODO: добавить 'Именины'
    heads = ['Международные', 'Национальные', 'Религиозные']
    table_position = soup.find('table', class_='infobox')
    next_silbings_list = list(table_position.fetchNextSiblings())

    for Id, child in enumerate(next_silbings_list):
        if child:
            if child.name:
                content = child.text.strip()
                try:
                    if child.name == "h3":  # тэг заголовка
                        head = get_emoji([h for h in heads if h in content][0])  # проверка и фильтрация заголовка
                        holiday_text += head + "\n\t" + get_head_values(next_silbings_list[(Id + 1):])
                    # тэг/текст, после которого идут уже ненужные значения
                    elif child.text == 'События[править | править код]':
                        break
                except IndexError:
                    pass
    return holiday_text


def get_holiday(date=None):
    url = "https://ru.wikipedia.org/wiki/{}"
    if type(date) == dict:
        return date['error']

    elif date:
        CURRENT_DATE = date

    else:
        now = str(datetime.now().strftime("%d %m"))
        CURRENT_DATE = regex_date(now)
    return get_data(get_html(url.format(CURRENT_DATE)))


if __name__ == '__main__':
    get_holiday()
