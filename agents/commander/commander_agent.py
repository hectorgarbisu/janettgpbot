from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import urllib.request


class CommanderAgent:
    
    def __init__(self):
        self.command_list = '\n'.join([
            '/ip: show my ip',
            '/hi: says hi',
        ])
            

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

    def ip(self, bot, update):
        ''' Says my internet ip '''
        update.message.reply_text(self.request_ip())

    def request_ip(self):
        try:
            return urllib.request.urlopen('https://ident.me').read().decode('utf8')
        except error:
            return 'The ip is a lie! ' + str(error)

    