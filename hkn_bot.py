#########################################################################################################
### HKN Telegram Bot. This is the code for the official bot of the Mu Nu Chapter of IEEE Eta Kappa Nu ###
#########################################################################################################

import os
import telegram
from telegram.ext import Updater
import filters
import time
import datetime


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

#-- Study groups handler
def tutoring(bot, update):
    for stringa in tutor.keys():
        bot.send_message(chat_id=update.message.chat_id, text=tutor[stringa])
   
filter_tutoring = filters.FilterTutoring()
tutoring_handler = MessageHandler(filter_tutoring, tutoring)
dispatcher.add_handler(tutoring_handler)

#-- About handler
def about(bot, update):
    in_file = open("about.txt", "r")
    bot.send_message(chat_id=update.message.chat_id, text=in_file.read())

filter_about = filters.FilterAbout()
about_handler = MessageHandler(filter_about, about)
dispatcher.add_handler(about_handler)


#-- News handler
class News:
    title = 'A title'
    content = 'Text'
    date = datetime.date(1943,3,13)  #year, month, day
    #print(date.strftime("%A"))
    def __init__(self, title, content, date):
        self.title = title
        self.content = content
        self.date = date

# demo datas
news1 = News(title='News 1', content='Lorem ipsum dolor sit', date=datetime.date(2018,3,13))
news2 = News(title='News 2', content='Consectetur adipiscing elit', date=datetime.date(2018,12,25))
newsList = [news1, news2]

def fetch_news(bot, update):
    for theNews in newsList:
        bot.send_message(chat_id=update.message.chat_id, text=theNews.content)


#-- Event handler
class Event:
    title = 'A title'
    description = 'Text'
    date = datetime.date(1943,3, 13)  #year, month, day
    def __init__(self, title, description, date):
        self.title = title
        self.description = description
        self.date = date

# demo datas
event1 = Event(title='Event 1', description='Evento di marzo (passato)', date=datetime.date(2018,3,13))
event2 = Event(title='Event 2', description='Evento di dicembre', date=datetime.date(2018,12,25))
eventList = [event1, event2]

def fetch_events(bot, update):
    for theEvent in eventList:
        todayDate = datetime.datetime.now()
        if theEvent.date >= todayDate: #do not print past events
            bot.send_message(chat_id=update.message.chat_id, text=theEvent.description)



updater.start_polling()
