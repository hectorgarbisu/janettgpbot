from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import urllib.request


def validate(fn):
    def wrapper(self, bot, update):
        chat_id = str(update.message.chat_id)
        if chat_id not in self.allowed_users:
            return update.message.reply_text('User not allowed');
        return fn(self, bot, update)
    return wrapper

class CommanderAgent:
    
    def __init__(self, allowed_users_file='data/allowed_users.txt'):
        self.allowed_users = self.allowed_users_from_file(allowed_users_file)
        self.command_list = '\n'.join([
            '/ip: show my ip',
            '/hi: says hi',
        ])
    
    def allowed_users_from_file(self, allowed_users_file):
        with open(allowed_users_file, 'r') as file:
            user_ids = {line.strip() for line in file}
            return user_ids

    def handlers(self):
        return [ 
                CommandHandler('commanderhelp', self._help),
                CommandHandler('ip', self.ip),
                CommandHandler('hi', self.hi),
            ]

    def _help(self, bot, update):
        '''Send a message when the command /help is issued.'''
        update.message.reply_text('Commander commands:\n' + self.command_list)
   
    def hi(self, bot, update):
        ''' Says hi '''
        update.message.reply_text('Hi!')

    @validate
    def ip(self, bot, update):
        ''' Says my internet ip '''
        update.message.reply_text(self.request_ip())

    def request_ip(self):
        try:
            return urllib.request.urlopen('https://ident.me').read().decode('utf8')
        except error:
            return 'The ip is a lie! ' + str(error)
