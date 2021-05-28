import requests
import re
from bs4 import BeautifulSoup

r = requests.get("https://ru.wikipedia.org/wiki/17_марта")
soup = BeautifulSoup(r.text, 'lxml')

div = soup.find('table', class_='infobox')

for id, tag in enumerate(div.fetchNextSiblings()):
    # print(tag.name, '-->', tag)
    regex_tag = re.findall('<ul>|<li/>', str(tag))
    if regex_tag:
        regex_tag








def pass_it():
    def iter_pass():
        text_values = []
        try:
            for count in range(len(recurive_child_gen_list)):

                pattern = recurive_child_gen_list[id + count]
                regex_tag = re.findall('<ul>|<li/>|mw-headline', str(pattern))

                if regex_tag:
                    if pattern.text.strip() not in heads:
                        if "h3" != pattern.name:
                            # заголовок тэга разделенного на двоеточие
                            duplicate_head = pattern.text.split(':')[0].strip()
                            # если заголовок уже есть в text_values, значит уже идут дупликаты
                            if not [k for k in text_values if duplicate_head in k]:
                                text_values.append(pattern.text)
                try:
                    # если следующий тэг h3,
                    # то возращаем форматированный текст с заголовком и его списком значений
                    if "h3" == pattern.name:
                        # print(f"-------------------------------------------------------------"
                        #       f"окончание ключа {head.upper()} на тэге {pattern.name.upper()}"
                        #       f"-------------------------------------------------------------")
                        return get_format_text(text_values, head)
                except TypeError:
                    pass
                count += 1
        except IndexError:
            pass

    def format():
        vals = str(raw_row).strip("['']").split('\\n')
        text = "\n" + get_emoji(head) + ':' + '\n\t'
        regex = "\(.*\)|(\[.*\]|\[.*[.\s;,])" \
                "\\xa0|\\\\|xa0"
        vals = [re.sub(regex, " ", v) for v in vals]


        values_head = []
        for id, v in enumerate(vals):
            tag_split_val = str(v).strip("['']").split('[править | править код]')
            dash_split_val = str(v).strip("['']").split('—')
            coln_split_val = str(v).strip("['']").split(':')
            if v in values_head:
                pass

            if len(tag_split_val) > 1:
                tx, vls = iter_dict(vals, tag_split_val, "[править | править код]")
                text += tx
                [values_head.append(v) for v in vls]


            else:
                # для значений через тире
                if len(dash_split_val) > 1:
                    enumarate_val = dash_split_val[0].replace('\\xa0', '')
                    args = dash_split_val[1].split('\n')[0]
                    text += f"{get_emoji(enumarate_val)} - {args} \n\t"

                # для значений через двоеточие
                elif len(coln_split_val) > 1:
                    tx, vls = iter_dict(vals, coln_split_val, '—')
                    text += tx
                    [values_head.append(v) for v in vls]

                else:
                    text += v + "\n\t"

        return text





    for id, child in enumerate(recurive_child_gen_list):
        if child:
            if child.name:
                content = child.contents
                try:
                    if "mw-headline" in child['class']:  # тэг заголовка
                        head = str([h.strip() for h in heads if h in content[-1]]).strip("'[]'")
                        if head:  # отфильтрованный заголовок
                            holiday_text += iteration_recurive(child, id)


                except KeyError:
                    pass

    return holiday_text
