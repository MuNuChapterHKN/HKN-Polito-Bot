import os
import telegram
from telegram.ext import Updater

print(os.environ['HKN_BOT_TOKEN'])
updater = Updater(token = os.environ['HKN_BOT_TOKEN'])

dispatcher = updater.dispatcher

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")
    
   
tutor = {'elettrotecnica' : 'tutoring di elettrotecnica il 30/11/2018', 'algoritmi' : 'tutoring di algoritmi e programmazione il 26/11/2018'}

def tutoring(bot, update):
   for stringa in tutor.keys():
      bot.send_message(chat_id=update.message.chat_id, text=tutor[stringa])

from telegram.ext import CommandHandler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

tutoring_handler = CommandHandler('tutoring', tutoring)
dispatcher.add_handler(tutoring_handler)

updater.start_polling()

