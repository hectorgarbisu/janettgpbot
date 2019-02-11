# Detects spanish date-like strings
# -*- coding: utf-8 -*-

import sys
import datetime
from . import date_utils as du
from collections import namedtuple 

class StateMachine(object):
    """ Previous state is used to allow dates so that
     "el jueves" wont fire a positive answer if its part of
     a larger date such as "el jueves de la semana que viene" 
    """
    def __init__(self):
        self.datetuple =  namedtuple("Date", 'year month day')
        self.date = datetime.date.today()
        self.temp_date = self.datetuple(year = self.date.year,
                                    month = self.date.month,
                                    day = self.date.year)
        self.current_state = "S0"
        self.previous_state = "S0"
        self.terminal_states = "SF SM4 SM5 SM_2 S5_2_1 S8 S13 S2 S3 S4 S5 S6 SM7".split()

    def transit(self, token):
        self.previous_state = self.current_state
        self.current_state = eval("self." + self.current_state)(token)

    def is_terminal(self):
        return (self.previous_state in self.terminal_states
                and self.current_state == "S0")
    # _

    def S0(self, token):
        if token in ["el", "este"]:
            return "S7"
        if token == u'mañana':
            self.date = datetime.date.today() + datetime.timedelta(days=1)
            return "S8"
        if token == u'hoy':
            self.date = datetime.date.today()
            return "S8"
        if token.endswith("a") and not token in ["para", "toca", "hola"]:
            return "S9"
        if token == "pasado":
            return "S13"
        if du.is_month_day(token):
            self.temp_date = self.datetuple(self.temp_date.year, self.temp_date.month, int(token))
            return "S11"
        if du.is_date(token):
            self.date = du.str_to_date(token)
            return "SF"
        return "S0"

    # mañana _ | hoy _
    def S8(self, token):
        return "S0"

    # el próximo _
    def S1(self, token):
        if token in ["dia", u"día"]:
            return "S3"
        if token in du.week_day:
            self.date = du.next_weekday_to_date(token)
            return "S2"
        if du.is_month_day(token):
            self.temp_date = self.datetuple(self.temp_date.year, self.temp_date.month, int(token))
            return "S3"
        return "S0"

    # el próximo martes _
    def S2(self, token):
        if du.is_month_day(token):
            self.temp_date = self.datetuple(self.temp_date.year, self.temp_date.month, int(token))
            return "S3"
        return "S0"

    # el próximo month_day _
    def S3(self, token):
        if token in ["de", "del"]:
            return "SM"
        return "S0"

    # el [día] [martes] cuatro|4 _
    def S4(self, token):
        if token in ["de", "del"]:
            return "SM"
        return "S0"

    # el jueves _
    def S5(self, token):
        if token == "de":
            return "S5_1"
        if token == "que":
            return "S5_4"
        if du.is_month_day(token):
            self.temp_date = self.datetuple(self.temp_date.year, self.temp_date.month, int(token))
            return "S4"
        if du.is_date(token):
            self.date = du.str_to_date(token)
            return "SF"
        return "S0"

    # _ semana que viene 
    def S5_1(self, token):
        if token == "esta":
            return "S5_2_1"
        if token == "la":
            return "S5_2"
        return "S0"

    def S5_2_1(self, token):
        return "S0"

    def S5_2(self, token):
        if token == "semana":
            return "S5_3"
        return "S0"

    def S5_3(self, token):
        if token == "que":
            return "S5_4"
        return "S0"

    # esta/la semana que _
    def S5_4(self, token):  # de la semana que viene, el domingo que viene
        if token == "viene":
            return "S6"
        return "S0"

    # la semana que viene _
    def S6(self, token):
        self.date = self.date + datetime.timedelta(days=7)
        return "S0"
    
    # el|este _
    def S7(self, token):
        if token in [u"día", "dia"]:
            return "S7"
        if du.is_date(token):
            self.date = du.str_to_date(token)
            return "SF"
        if du.is_month_day(token):
            self.temp_date = self.datetuple(self.temp_date.year, self.temp_date.month, int(token))
            return "S4"
        if token in [u"próximo", "proximo"]:
            return "S1"
        if token in du.week_day:
            self.date = du.this_weekday_to_date(token)
            return "S5"
        return "S0"

    # dd/mm
    # dd/mm/yy
    # dd/mm/yyyy
    def SF(self, token):
        return "S0"
    
    # 11 _
    def S11(self, token):
        if token == "de":
            return "S11_1"
        return "S0"
    
    # 11 de _
    def S11_1(self, token):
        if du.is_month(token):
            self.temp_date = self.datetuple(self.temp_date.year, int(token), self.temp_date.day)
            return "SM4"
        return "S0"

    # maldit(a)
    def S9(self, token):
        return "S0"

    # pasado _
    def S13(self, token):
        if token == u"mañana":
            self.date = self.date + datetime.timedelta(days=2)
        if token == u"pasado":
            return "S13"
        return "S0"

    # el día cuatro de _
    def SM(self, token):
        if du.is_month(token):
            self.temp_date = self.datetuple(self.temp_date.year, int(token), self.temp_date.day)
            return "SM4"
        if token == "mes":
            return "SM_1"
        return "S0"

    # del mes _
    def SM_1(self, token):
        if token == "que":
            return "SM_2"
        return "S0"
    
    # del mes que viene _
    def SM_2(self, token):
        if token == "viene":
            self.date = du.add_months(self.date, 1)
        return "S0"

    # el día cuatro de octubre
    # el 3 del 02
    def SM4(self, token):
        if token in ["de", "del"]:
            return "SM5"
        self.date = datetime.date(*self.temp_date) 
        return "S0"

    # el 3 del 01 del _
    def SM5(self, token):
        if du.is_year(token):
            self.date = datetime.date(*self.temp_date)
        return "S0"


def get_date(msg):
    trash_chars = ',.!ç?¿/:'
    tokens = (msg + " padding ").split()
    sm = StateMachine()
    trace = []
    if len(tokens) < 2:
        return (None, trace)
    for token in tokens:
        trace.append(sm.current_state)
        sm.transit(token.strip(trash_chars))
        if sm.is_terminal():
            return (sm.date, trace)

    return (None, trace)

def test():
    from colorama import init, Fore, Style
    init(convert=True)
    mensajes_fechados = \
        [u"MENSAJES CON FECHA: dos de abril:",
         u" dos de abril ",
         u" el cinco de mayo tengo clase de canto ",
         u" mañana tendré hambre, mucha mucha mucha",
         u" el día seis de mayo tengo clase de canto otra vez ",
         u" el lunes de esta semana ",
         u" el día 3 tengo que bailar la macarena",
         u" el lunes de la semana que viene papitas ",
         u" el 04/01 del año que viene milagritos++",
         u" el lunes te cuento el chiste",
         u" y mañana tengo más deberes",
         u" el 3 de marzo ",
         u" para mañana ",
         u" este día cinco blup",
         u" este domingo",
         u" para pasado mañana ",
         u" el 4 del mes que viene ",
         u" el próximo domingo blep",
         u" el domingo fiesta",
         u" pasado mañana almuerzo con mis padres",
         u" el jueves primero de enero ",
         u" el 20 de junio de 1990 no estuvo nada mal",
         u" el 20/06/1990 no estuvo nada mal",
         u"habrá risas y fiestas hoy por la noche"
         ]

    mensajes_no_fechados = \
        [u"MENSAJES SIN FECHA",
         u" puta mañana, cómo duele",
         u" el mañana nunca muere ",
         u" hola buenas  ",
         u" el tres de corazones",
         u" el 3 de 05spadas",
         u" el cuarto número es el 3",
         u" el 4º número es el 4 segun matlab",
         u" matlab está loco ",
         u" tres veces te engañé ",
         u" mensaje_demasiado_corto",
         u" en octubre te fuiste",
         u" 1994 fué, por verdad usuluta, el mejor año de la historia",
         u" aunque junio de 1990 no estuvo nada mal "
         ]

    for ii in mensajes_fechados:
        (date, trace) = get_date(ii)
        color = Fore.GREEN if date else Fore.RED
        print(color + ii + Style.RESET_ALL)
        print(trace, date)

    for ii in mensajes_no_fechados:
        (date, trace) = get_date(ii)
        color = Fore.RED if date else Fore.GREEN
        print(color + ii + Style.RESET_ALL)
        print(trace, date)

if __name__ == "__main__":
    test()
