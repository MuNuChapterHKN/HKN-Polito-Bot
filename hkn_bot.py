import os
import telegram
from telegram.ext import Updater

print(os.environ['HKN_BOT_TOKEN'])
updater = Updater(token = os.environ['HKN_BOT_TOKEN'])

dispatcher = updater.dispatcher

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()

