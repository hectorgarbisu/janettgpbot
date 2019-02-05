
# -*- coding: utf-8 -*-
import datetime
import re
import time

months = "enero febrero marzo abril mayo junio julio agosto septiembre setiembre octubre noviembre diciembre".split()
month_indices = [1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 10, 11, 12]
cardinal_month = [str(x+1) for x in range(12)]
week_day = u"lunes martes miercoles miércoles jueves viernes sabado sábado domingo".split()
week_day_indices = [0, 1, 2, 2, 3, 4, 5, 5, 6]
cardinal_month_day = [str(x+1) for x in range(31)]
written_month_day = u"""uno primero dos segundo tres tercero cuatro cuarto cinco quinto seis sexto
siete séptimo septimo ocho octavo nueve noveno diez décimo decimo once undécimo decimoprimero decimoprimer
doce duodécimo decimosegundo trece catorce quince dieciséis dieciseis diecisiete dieciocho diecinueve veinte
veintiuno veintidos veintitres veinticuatro veinticinco veintiseis veintisiete veintiocho veintinueve treinta""".split()
written_month_day_indices = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 7, 8, 8, 9, 9, 10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 13,
                             14, 15, 16, 16] + [a for a in range(17, 31)]


def next_weekday_to_date(string):
    twd = this_weekday_to_date(string)
    date = twd + datetime.timedelta(days=7)
    return date


def is_year(token):
    def is_numeral(string):
        return all(str.isdigit(char) for char in str(token))
    if not is_numeral(token):
        return False
    num = int(token)
    return 1900 < num < 2100 or 0 < num < 100


def update_year(prev_date, token):
    return datetime.date(int(token), prev_date.month, prev_date.day)


def add_months(prev_date, num):
    carry = (prev_date.month + num)//12
    new_date = datetime.date(prev_date.year + carry,
                             (prev_date.month + num) % 12,
                             prev_date.day)
    return new_date


def this_weekday_to_date(string):
    today = datetime.date.today()
    day_idx = dict(zip(week_day, week_day_indices))[string.lstrip("0")]
    diff = day_idx - today.weekday()
    date = today + datetime.timedelta(days=diff)
    return date


def update_month(prev_date, token):
    tkn = re.sub('[^a-zA-Z0-9-_*.]', '', token).lstrip("0")
    month = dict(zip(months + cardinal_month,
                     month_indices + cardinal_month))[tkn]
    return datetime.date(prev_date.year, int(month), prev_date.day)


def update_month_day(date, string):
    today = datetime.date.today()
    day_idx = dict(zip(written_month_day+cardinal_month_day,
                       written_month_day_indices+cardinal_month_day))[string.lstrip("0")]
    return datetime.date(today.year, today.month, int(day_idx))

def is_month(token):
    return re.sub('[^a-zA-Z0-9-_*.]', '', token) in months or token.lstrip("0") in [str(x) for x in range(1, 13)]


def is_month_day(string):
    return string.lstrip("0") in cardinal_month_day + written_month_day

def date_to_string(date):
    return "{}/{}/{}".format(date.day, date.month, date.year)

def replace_all(string, chars, final_char):
    new_string = string
    for char1, char2 in zip(chars, chars[1::]):
        new_string = new_string.replace(char1, char2)
    return new_string.replace(chars[-1], final_char)


def is_date(string):
    tokens = replace_all(string, ['/', '-', ':', ',', '.'], " ").split()
    if len(tokens) == 2:
        if(is_month_day(tokens[0]) and is_month(tokens[1])):
            return True
    elif len(tokens) == 3:
        if(is_month_day(tokens[0]) and is_month(tokens[1]) and is_year(tokens[2])):
            return True
    return False


def str_to_date(string):
    tokens = replace_all(string, ['/', '-', ':', ',', '.'], " ").split()
    current_year = tokens[2] if len(
        tokens) == 3 else datetime.date.today().year
    return datetime.date(int(current_year), int(tokens[1]), int(tokens[0]))

def test():
    today = datetime.date.today()
    print(today)
    print(this_weekday_to_date("martes"))
    print(next_weekday_to_date("martes"))
    day23 = update_month_day(today, "23")
    print(day23)
    print(add_months(today, 1))
    print(is_month("1"), is_month("01"), is_month("febrero"), is_month("roca"))
    print(update_month(today, "5"))
    print(is_year("2994"), is_year("2018"), is_year("cuatro"))
    print(is_date("23-234/23"), is_date("23-4/23"), is_date("01/04"))
    print(str_to_date("23/04"), str_to_date("23-4-2020"))
    print(date_to_string(str_to_date("10/10/10")))

if __name__ == "__main__":
    test()