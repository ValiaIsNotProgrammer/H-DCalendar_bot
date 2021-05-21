from datetime import datetime

def regex_date(raw):

    errors_dict = dict()
    list_month = ['января','февраля','марта','апреля','мая','июня','июля',
                  'августа','сентября','октября','ноября','декабря']

    def correct_format_date(month, number):
        for id_,m in enumerate(list_month):
            if month == m:
                date = "_".join(list([number,m]))
                id_month = id_+1
                break
            elif month in m:
                print(f'{month} corrected to {m}')
                date = "_".join(list([number, m]))
                id_month = id_ + 1
                break
            elif id_ == 11:
                errors_dict['error'] = "Uncorrect month"
                return errors_dict

        if len(' '.join(str(id_)).split(' ')) == 1:
            id_month = '0' + str(id_month)

        date_format = "{}/{}".format(number,id_month)
        try:
            datetime.strptime(date_format, '%d/%m')
            return date
        except ValueError:
            errors_dict['error'] = 'Uncorrect number'
            return errors_dict

    def split(txt):
        seps = ' '.join("/:;.\'\",-%#\\").split(' ')
        original_txt = txt
        default_sep = seps[0]

        # we skip seps[0] because that's the default separator
        for sep in seps[1:]:
            txt = txt.replace(sep, default_sep)
        splt_txt = [i.strip() for i in txt.split(default_sep)]
        if str(splt_txt).strip("'[]'") == original_txt:
            return original_txt.split(' ')
        return splt_txt

    def language_date(dt=None):
        if dt is None:
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


    raw = split(raw)
    if len(raw) != 2:
        errors_dict['error'] = 'Uncorrect format'
        return errors_dict

    if ( raw[0].isdigit() & raw[1].isdigit() ):
        raw_date = '/'.join(raw)
        raw_date = datetime.strptime(raw_date, '%d/%m').ctime().split()
        date = language_date(raw_date[1:3])
        date = "_".join(list(date))
        return date

    elif ( raw[0].isdigit() & ( not raw[1].isdigit() ) ):
        month = raw[1].lower()
        number = raw[0]
        return correct_format_date(month, number)

    elif ( raw[1].isdigit() & ( not raw[0].isdigit() ) ):
        month = raw[0].lower()
        number = raw[1]
        return correct_format_date(month, number)

    else:
        errors_dict['error'] = 'Sorry, at least one value must be numeric'
        return errors_dict








