
import calendar
import datetime
import time
from calendar import monthrange
import pickle
from . import date_utils as du
# Stores and retrieves events at specific days, months, years, or weeks


class Calendar(object):

    def __init__(self, chat_id="default"):
        self.calendar_path = "./data/calendar_object_" + chat_id + ".dat"
        #days_from_epoch = int(time.mktime(datetime.date.today().timetuple()))/(24*60*60)
        self.load_from_disk()

    def load_from_disk(self):
        try:
            calendar_file = open(self.calendar_path, 'rb')
            self.events = pickle.load(calendar_file)
        except:
            self.events = {}

    def save_to_disk(self):
        with open(self.calendar_path, 'wb') as calendar_file:
            pickle.dump(self.events, calendar_file)

    def add_event(self, event="", date=datetime.date.today()):
        """ add_event (event, date): saves string event at date """
        if date in self.events:
            self.events[date].append(event)
        else:
            self.events[date] = [event]

    def get_this_week(self):
        days_from_monday = datetime.date.today().weekday()
        monday = datetime.date.today() - datetime.timedelta(days=days_from_monday)
        return self.get_days(7, monday)

    def get_this_month(self):
        today = datetime.date.today()
        return self.get_days(monthrange(today.year, today.month)[1], datetime.date(today.year, today.month, 1))

    def get_all(self):
        all_days = ""
        for date, events in self.events.items():
            all_days += du.date_to_string(date) + " : " + str(events) + "\n"
        return all_days

    def get_days(self, days=1, from_day=datetime.date.today()):
        lapse = ""
        for ii in range(days): 
            delta = datetime.timedelta(days=ii)
            day = from_day + delta
            if day in self.events:
                lapse += "{} : {} \n".format(du.date_to_string(day), str(self.events[day]))
        return lapse

    def delete_all(self):
        self.events.clear()

    def delete_old(self):
        self.events = {k: v for k, v in self.events.items() if k >
                       datetime.date.today()}


def test():
    cal = Calendar()
    cal.delete_all()
    cal.save_to_disk()    
    today = datetime.date.today()
    cal.add_event(" esto es un evento ", today)
    cal.add_event(" esto es otro evento el mismo dia", today)
    cal.add_event(" esto es otro evento otro dia", datetime.date(2018, 10, 14))
    cal.add_event(" evento de ayer ", today + datetime.timedelta(days=-1))
    cal.add_event(" evento de principios de mes  ",
                  datetime.date(today.year, today.month, 1))
    cal.add_event(" evento de final de mes  ", datetime.date(2018, 10, 31))
    cal.add_event(" evento de otro mes  ", datetime.date(2018, 11, 1))
    print(cal.events)
    print(cal.get_this_week())
    print(cal.get_this_month())
    print(cal.get_days(20))
    cal.delete_old()
    print(cal.events)
    cal.save_to_disk()
    cal.delete_all()
    print(cal.events)
    cal.load_from_disk()
    print(cal.events)
    print(cal.get_all())


if __name__ == "__main__":
    test()
