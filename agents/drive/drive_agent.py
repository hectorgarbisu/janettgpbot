from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from time import sleep
import os
from .drive_uploader import DriveUploader
import logging

class DriveAgent:

    def __init__(self):
        self.drive = DriveUploader()
        self.drive.auth()
        with open('./data/folder_id', 'r') as folder_id_file:
            FOLDER_ID = folder_id_file.read()
        self.drive.set_folder(FOLDER_ID)


    def help(self, bot, update):
        """Send a message when the command /help is issued."""
        update.message.reply_text('Lista de comandos:\n' + command_list)


    def echo(self, bot, update):
        """Echo the user message."""
        update.message.reply_text(update.message.text)

    def upload_named_file(self, bot, update, file_id, file_name):
        newFile = bot.get_file(file_id)
        newFile.download(file_name)
        self.drive.upload_file(file_name)
        update.message.reply_text(f'Uploaded {file_name}')
        os.remove(file_name)

    def upload_unnamed_file(self, bot, update, file_id, chronological_filename):
        file_name = ""
        while not file_name or os.path.exists(file_name):
            sleep(1)
            file_name = chronological_filename()
        self.upload_named_file(bot, update, file_id, file_name)


    def document(self, bot, update):
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name
        update.message.reply_text(f'document file received {file_name}')
        self.upload_named_file(bot, update, file_id, file_name)


    def audio(self, bot, update):
        file_id = update.message.audio.file_id
        file_name = update.message.audio.file_name
        update.message.reply_text(f'audio file received {file_name}')
        self.upload_named_file(bot, update, file_id, file_name)


    def photo(self, bot, update):
        file_id = update.message.photo[-1]
        self.upload_unnamed_file(bot, update, file_id, self.photo_filename)

    def video(self, bot, update):
        file_id = update.message.video.file_id
        update.message.reply_text(f'video file received {file_id}')
        self.upload_unnamed_file(bot, update, file_id, self.video_filename)

    def video_note(self, bot, update):
        file_id = update.message.video_note.file_id
        update.message.reply_text(f'video_note received {file_id}')
        self.upload_unnamed_file(bot, update, file_id, self.video_filename)

    def voice_note(self, bot, update):
        file_id = update.message.voice.file_id
        update.message.reply_text(f'voice_note received {file_id}')
        self.upload_unnamed_file(bot, update, file_id, self.audio_filename)



    def photo_filename(self):
        return f'photo_{self.now_substring()}.jpg'

    def video_filename(self):
        return f'video_{self.now_substring()}.mp4'

    def audio_filename(self):
        return f'audio_{self.now_substring()}.ogg'



    def now_substring(self):
        #example string image_2019-01-14_16-01-20.png"
        format_string = "%Y-%m-%d_%H-%M-%S"
        return datetime.now().strftime(format_string)


    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)


    def handlers(self):
        return [
            MessageHandler(Filters.text, self.echo),
            MessageHandler(Filters.document, self.document),
            MessageHandler(Filters.video, self.video),
            MessageHandler(Filters.audio, self.audio),
            MessageHandler(Filters.voice, self.voice_note),
            MessageHandler(Filters.video_note, self.video_note),
            MessageHandler(Filters.photo, self.photo),
        ]

