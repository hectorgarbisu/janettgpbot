# -*- coding: utf-8 -*-
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
from agents import agents

def start(bot, update):
    """Send a message when the command /start is issued."""
    chat_id = str(update.message.chat_id)
    update.message.reply_text(f'Tu eres {chat_id}')

def add_handlers(dp, agent):
    handlers = agent.handlers()
    print(handlers)
    for handler in handlers:
        dp.add_handler(handler)

def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.

    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    logger = logging.getLogger(__name__)

    with open('./data/apikey', 'r') as apikey_file:
        TOKEN = apikey_file.read()

    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    for agent in agents:
        add_handlers(dp, agent)

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))

    """
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))
    dp.add_handler(MessageHandler(Filters.text, texto))

    # Button handler
    dp.add_handler(CallbackQueryHandler(button))

    # log all errors
    dp.add_error_handler(error)
    """

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
