
# -*- coding: utf-8 -*-
import datetime
import re
import time

months = "enero febrero marzo abril mayo junio julio agosto septiembre setiembre octubre noviembre diciembre".split()
month_indices = [1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 10, 11, 12]
cardinal_month = [str(x+1) for x in range(12)]
week_day = u"lunes martes miercoles miércoles jueves viernes sabado sábado domingo".split()
week_day_indices = [0, 1, 2, 2, 3, 4, 5, 5, 6]
cardinal_month_day = [str(x+1) for x in range(32)]
written_month_day = u"""uno primero dos segundo tres tercero cuatro cuarto cinco quinto seis sexto
siete séptimo septimo ocho octavo nueve noveno diez décimo decimo once undécimo decimoprimero decimoprimer
doce duodécimo decimosegundo trece catorce quince dieciséis dieciseis diecisiete dieciocho diecinueve veinte
veintiuno veintidos veintitres veinticuatro veinticinco veintiseis veintisiete veintiocho veintinueve treinta treintayuno""".split()
written_month_day_indices = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 7, 8, 8, 9, 9, 10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 13,
                             14, 15, 16, 16] + [a for a in range(17, 32)]

class DateTuple():
    """ 
    Statefull representation of a date to handle incremental change
    for example: 11 feb 2019 -> 30 May 2019 might first set the day to 30
    and then the month to may. 30 feb is not a valid date, but a valid temporal DateTuple
    """
    def __init__(self, date = datetime.date.today()):
        self.day = date.day
        self.month = date.month
        self.year = date.year

    def __add__(self, other):
        if type(other) is datetime.timedelta:
            diff = other
        elif type(other) is int:
            diff = datetime.timedelta(days = other)
        date = self.as_date() + diff
        self._set(date)

    def _set(self, date):
        self.day = date.day
        self.month = date.month
        self.year = date.year

    def as_date(self):
        return datetime.date(self.year, self.month, self.day)

    def set_month(self, token):
        self.month = parse_month(token)

    def set_day(self, token):
        self.day = parse_day(token)

    def set_year(self, token):
        self.year = int(token)

    def set_date(self, date):
        if type(date) == str:
            date = str_to_date(date)
        elif type(date) == datetime.date:
            self._set(date)
    
    def set_this_weekday(self, weekday):
        date = this_weekday_to_date(weekday)
        self._set(date)

    def set_next_weekday(self, weekday):
        date = DateTuple(next_weekday_to_date(weekday))
        self._set(date)

    def add_months(self, months):
        as_date = self.as_date()
        new_date = add_months(as_date, months)
        self._set(new_date)

def today_tuple():
    return DateTuple()

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


def parse_month(string):
    tkn = re.sub('[^a-zA-Z0-9-_*.]', '', string).lstrip("0")
    month = dict(zip(months + cardinal_month,
                     month_indices + cardinal_month))[tkn]
    return int(month)

def parse_day(string):
    day_idx = dict(zip(written_month_day+cardinal_month_day,
                       written_month_day_indices+cardinal_month_day))[string.lstrip("0")]
    return int(day_idx)

def this_weekday_to_date(string):
    today = datetime.date.today()
    day_idx = dict(zip(week_day, week_day_indices))[string.lstrip("0")]
    diff = day_idx - today.weekday()
    date = today + datetime.timedelta(days=diff)
    return date


def update_month(prev_date, token):
    return datetime.date(prev_date.year, parse_month(token), prev_date.day)


def update_month_day(date, token):
    return datetime.date(date.year, date.month, parse_day(token))

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