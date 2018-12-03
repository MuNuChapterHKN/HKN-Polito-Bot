#########################################################################################################
### HKN Telegram Bot. This is the code for the official bot of the Mu Nu Chapter of IEEE Eta Kappa Nu ###
#########################################################################################################

import os
import telegram
from telegram.ext import Updater
import filters

# Uncomment for debug
#print(os.environ['HKN_BOT_TOKEN'])

# Retrieving bot token
updater = Updater(token = os.environ['HKN_BOT_TOKEN'])

dispatcher = updater.dispatcher

# Handling commands
from telegram.ext import CommandHandler

# Start command handler
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Benvenuto nel bot ufficiale di Eta Kappa Nu Polito!")
    

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)    

# Handling messages
from telegram.ext import MessageHandler

# Study groups informations  
tutor = {'elettrotecnica' : 'tutoring di elettrotecnica il 30/11/2018', 'algoritmi' : 'tutoring di algoritmi e programmazione il 26/11/2018'}

# Study groups handler
def tutoring(bot, update):
   for stringa in tutor.keys():
      bot.send_message(chat_id=update.message.chat_id, text=tutor[stringa])
   
filter_tutoring = filters.FilterTutoring()
tutoring_handler = MessageHandler(filter_tutoring, tutoring)
dispatcher.add_handler(tutoring_handler)

#about handler
def about(bot, update):
   in_file = open("about.txt", "r")
   bot.send_message(chat_id=update.message.chat_id, text=in_file.read())

filter_about = filters.FilterAbout()
about_handler = MessageHandler(filter_about, about)
dispatcher.add_handler(about_handler)


updater.start_polling()

