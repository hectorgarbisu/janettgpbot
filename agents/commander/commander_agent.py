from io import StringIO
import sys
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import urllib.request
from agents.commander.tide_command.tides_from_harmonics import get_current_day_forecast

def restricted(fn):
    def wrapper(self, bot, update, *args, **kwargs):
        chat_id = str(update.message.chat_id)
        if chat_id not in self.allowed_users:
            return update.message.reply_text('User not allowed');
        return fn(self, bot, update, *args, **kwargs)
    return wrapper

class CommanderAgent:

    def __init__(self, allowed_users_file='data/allowed_users.txt'):
        self.allowed_users = self.allowed_users_from_file(allowed_users_file)
        self.command_list = '\n'.join([
            '/ip: show my ip',
            '/hi: says hi',
            '/python <expr>: evaluates a python expresion "expr"'
            '/py <expr>: same as /python <expr>'
        ])

    def handlers(self):
        return [ 
                CommandHandler('commanderhelp', self._help),
                CommandHandler('ip', self.ip),
                CommandHandler('hi', self.hi),
                CommandHandler('tide', self.tide),
                CommandHandler('tides', self.tide),
                CommandHandler('py', self.python, pass_args=True),
                CommandHandler('python', self.python, pass_args=True),
            ]

    @staticmethod
    def _eval_expression(expression):
        '''
        Return either the value of the expression if no value
        is found
        '''
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        return_value = str(eval(expression))
        printed_text = mystdout.getvalue()
        return f'{printed_text}\n>{return_value}'
        sys.stdout = old_stdout

    @staticmethod
    def _request_ip():
        try:
            return urllib.request.urlopen('https://ident.me').read().decode('utf8')
        except Exception as error:
            return 'The ip is a lie! ' + str(error)

    @staticmethod
    def _multi_reply(update, message, message_size=500):
        for i in range(0, len(message), message_size):
            chunk = message[i: message_size +i]
            update.message.reply_text(chunk)


    def allowed_users_from_file(self, allowed_users_file):
        with open(allowed_users_file, 'r') as file:
            user_ids = {line.strip() for line in file}
            return user_ids

    def _help(self, bot, update):
        '''Send a message when the command /help is issued.'''
        update.message.reply_text('Commander commands:\n' + self.command_list)
   
    def hi(self, bot, update):
        ''' Says hi '''
        update.message.reply_text('Hi!')

    @restricted
    def ip(self, bot, update):
        ''' Says my internet ip '''
        update.message.reply_text(self._request_ip())
    
    @restricted
    def python(self, bot, update, args=[]):
        '''
        Evaluates a python expression
        '''
        try:
            self._multi_reply(update, self._eval_expression(' '.join(args)))
        except Exception as error:
            update.message.reply_text(str(error))
    
    def tide(self, bot, update):
        ''' 
        Returns a representation of today's tides 
        '''
        update.message.reply_text(str(get_current_day_forecast(150)))