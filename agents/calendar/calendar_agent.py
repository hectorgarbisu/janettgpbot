from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
from .text_date_extractor import get_date
from .bot_calendar import Calendar


class CalendarAgent(object):
    
    def __init__(self):
        self.calendars = {}
        self.temp_date_dicts = {}
        self.command_list = "/start: no hace nada\n" +\
            "/semana: muestra los eventos de esta semana\n"+\
            "/mes: muestra los eventos de este mes\n"+\
            "/todo: muestra todos tus eventos\n"+\
            "/dias X: muestra los eventos entre hoy y dentro de X días\n"+\
            "/purgar_cola: elimina los eventos pendientes de confirmación\n"+\
            "/pendientes: muestra los eeventos almacenados sin confirmar\n"+\
            "/borrar_pasadas: elimina los eventos anteriores al día de hoy\n"+\
            "/borrar_todo: eliminna todos los eventos del calendario\n"
            

    def handlers(self):
        return [ 
                CommandHandler("calendarhelp", self._help),
                CommandHandler("semana", self.week),
                CommandHandler("mes", self.month),
                CommandHandler("todo", self.all),
                CommandHandler("dias", self.days, pass_args=True),
                CommandHandler("purgar_cola", self.clear_pending),
                CommandHandler("pendientes", self.show_pending),
                CommandHandler("borrar_pasadas", self.delete_old),
                CommandHandler("borrar_todo", self.delete_all),
                MessageHandler(Filters.text, self.texto),
                CallbackQueryHandler(self.button)
            ]
    
    def clear_pending(self, bot, update):
        """ Clears the list of pending dates to aprove """
        chat_id = str(update.message.chat_id)
        if self.temp_date_dicts[chat_id]:
            self.temp_date_dicts[chat_id].clear()
            update.message.reply_text("Cola de entradas purgada")


    def show_pending(self, bot, update):
        """ Shows the list of pending dates to aprove """
        chat_id = str(update.message.chat_id)
        if self.temp_date_dicts[chat_id]:
            response = ""
            for date_string, event in self.temp_date_dicts[chat_id]:
                response += "\n" + date_string + ": " + event
            update.message.reply_text(response)


    def delete_old(self, bot, update):
        chat_id = str(update.message.chat_id)
        if chat_id not in self.calendars:
            self.calendars[chat_id] = Calendar(chat_id)
            self.temp_date_dicts[chat_id] = {}
        self.calendars[chat_id].delete_old()
        self.calendars[chat_id].save_to_disk()
        update.message.reply_text("Eliminadas entradas anteriores a hoy")


    def delete_all(self, bot, update):
        chat_id = str(update.message.chat_id)
        if chat_id not in self.calendars:
            self.calendars[chat_id] = Calendar(chat_id)
            self.temp_date_dicts[chat_id] = {}
        self.calendars[chat_id].delete_all()
        self.calendars[chat_id].save_to_disk()
        update.message.reply_text("Eliminadas todas las entradas")


    def days(self, bot, update, args):
        """ retrieves events for the following days """
        chat_id = str(update.message.chat_id)
        if chat_id not in self.calendars:
            self.calendars[chat_id] = Calendar(chat_id)
            self.temp_date_dicts[chat_id] = {}
        days = 1
        if len(args): days = int(args[0])
        days_events = self.calendars[chat_id].get_days(days)
        if days_events:
            update.message.reply_text(days_events)


    def week(self, bot, update):
        """ retrieves current week events """
        chat_id = str(update.message.chat_id)
        if chat_id not in self.calendars:
            self.calendars[chat_id] = Calendar(chat_id)
            self.temp_date_dicts[chat_id] = {}
        this_weeks_events = self.calendars[chat_id].get_this_week()
        if this_weeks_events:
            update.message.reply_text(this_weeks_events)

    def all(self, bot, update):
        """ retrieves current week events """
        chat_id = str(update.message.chat_id)
        if chat_id not in self.calendars:
            self.calendars[chat_id] = Calendar(chat_id)
            self.temp_date_dicts[chat_id] = {}
        all_events = self.calendars[chat_id].get_all()
        if all_events: 
            update.message.reply_text(all_events)

    def month(self, bot, update):
        """ retrieves current month events """
        chat_id = str(update.message.chat_id)
        if chat_id not in self.calendars:
            self.calendars[chat_id] = Calendar(chat_id)
            self.temp_date_dicts[chat_id] = {}
        this_month_events = self.calendars[chat_id].get_this_month()
        if this_month_events:
            update.message.reply_text(this_month_events)


    def start(self, bot, update):
        """Send a message when the command /start is issued."""
        chat_id = str(update.message.chat_id) 
        self.calendars[chat_id] = Calendar(chat_id)
        self.temp_date_dicts[chat_id] = {}
        update.message.reply_text('Encendido')



    def _help(self, bot, update):
        """Send a message when the command /help is issued."""
        update.message.reply_text('Comandos de calendario:\n' + self.command_list)


    def echo(self, bot, update):
        """Echo the user message."""
        update.message.reply_text(update.message.text)


    def texto(self, bot, update):
        """ Handles text messages by trying to find a suitable date format. The first date-like
        structure is found, it is saved temporaryly in temp_date_dict, and is added to calendario
        upon confirmation by button  """
        chat_id = str(update.message.chat_id)
        if chat_id not in self.calendars:
            self.calendars[chat_id] = Calendar(chat_id)
            self.temp_date_dicts[chat_id] = {}
        msg = update.message.text.lower()
        (date, trace) = get_date(msg)
        if not date:
            return
        print(trace)
        msg_id = update.message.message_id
        self.temp_date_dicts[chat_id][msg_id] = (msg, date)
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Guardar en calendario", callback_data=msg_id)]])
        update.message.reply_text(self.response_text(
            msg, update, date), reply_markup=reply_markup)


    def response_text(self, msg, update, date):
        response = ""
        date_string = str(date.day) + "/" + str(date.month) + "/" + str(date.year)
        response += "posible fecha detectada para " + \
            update.message.from_user.first_name + "! : \n"
        response += date_string + " en :\n"
        response += msg
        return response


    def button(self, bot, update):
        """ Tries to save the corresponding date and event to calendario """
        #chat_id = str(update.callback_query.chat_id)
        chat_id = str(update.callback_query.message.chat.id)
        query = update.callback_query
        emmiter_msg_id = query.data
        event, date = self.temp_date_dicts[chat_id].pop(int(emmiter_msg_id))
        self.calendars[chat_id].add_event(event, date)
        self.calendars[chat_id].save_to_disk()
        date_string = str(date.day) + "/" + str(date.month) + "/" + str(date.year)
        bot.edit_message_text(text="Fecha guardada: {}".format(date_string),
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id)






    