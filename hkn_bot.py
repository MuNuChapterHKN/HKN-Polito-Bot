#########################################################################################################
### HKN Telegram Bot. This is the code for the official bot of the Mu Nu Chapter of IEEE Eta Kappa Nu ###
#########################################################################################################

import os
import telegram
import filters
from telegram.ext import Updater
# Handling commands
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
#tutoring part imports
import re
import html2text
from urllib.request import urlopen
#events - news import
import time
import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts

from functools import wraps
from telegram import ChatAction

def send_action(action):
    ## Sends `action` while processing func command

    def decorator(func):
        @wraps(func)
        def command_func(*args, **kwargs):
            bot, update = args
            bot.send_chat_action(chat_id=update.effective_message.chat_id, action=action)
            return func(bot, update, **kwargs)
        return command_func
    
    return decorator

# The message "is typing" appears while the bot is processing messages
send_typing_action = send_action(ChatAction.TYPING)

# Uncomment for debug
#print(os.environ['HKN_BOT_TOKEN'])

# Retrieving bot token
updater = Updater(token = os.environ['HKN_BOT_TOKEN'])

dispatcher = updater.dispatcher

# Start command handler
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Benvenuto nel bot ufficiale di Eta Kappa Nu Polito!")
    custom_keyboard = [['Events', 'News'], ['Study Groups', 'About HKN']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text="Scegli una di queste opzioni:", reply_markup=reply_markup)
    

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)    

# Study groups informations  
#not required anymore
#tutor = {'elettrotecnica' : 'tutoring di elettrotecnica il 30/11/2018', 'algoritmi' : 'tutoring di algoritmi e programmazione il 26/11/2018'}


#-- Study groups handler
@send_typing_action
def tutoring(bot, update):
    #old version:
    #for stringa in tutor.keys():
    #    bot.send_message(chat_id=update.message.chat_id, text=tutor[stringa])
    
    #new version:
    fp = urlopen("http://hknpolito.org/tutoring/")
    mybytes = fp.read()
    mystr = mybytes.decode("utf8")
    fp.close()
    mystr = html2text.html2text(mystr)
    m=mystr.split("* ###")
    m.pop(0)
    for el in m:
        sub_els=el.split('\n',7)
        sub_els.pop()
        sub_els=sub_els[2:]
        tutoring_block=""
        for sub_el in sub_els:
            tutoring_block=tutoring_block + "\n" + str.lstrip(sub_el,"#### ")
        bot.send_message(chat_id=update.message.chat_id, text=tutoring_block)
   
filter_tutoring = filters.FilterTutoring()
tutoring_handler = MessageHandler(filter_tutoring, tutoring)
dispatcher.add_handler(tutoring_handler)

# About handler
@send_typing_action
def about(bot, update):
    in_file = open("about.txt", "r", encoding="utf-8")
    bot.send_message(chat_id=update.message.chat_id, text=in_file.read())
    in_file.close()

filter_about = filters.FilterAbout()
about_handler = MessageHandler(filter_about, about)
dispatcher.add_handler(about_handler)


#-- Questions handler
@send_typing_action
def questions(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Fai una domanda al MuNu Chapter di Eta Kappa Nu")

filter_questions = filters.FilterQuestions()
questions_handler = MessageHandler(filter_questions, questions)
dispatcher.add_handler(questions_handler)

#-- Asnwer appender to file
# Answers must containts with "?"
def answers(bot,update):
    out_file = open("questions.txt","a+")
    out_file.write(str(update.message.from_user.username)+" - "+update.message.text+"\n")
    out_file.close()
    bot.send_message(chat_id=update.message.chat_id, text="La tua domanda è stata registrata, ti risponderemo a breve")
    

filter_answers = filters.FilterAnswers()
answers_handler = MessageHandler(filter_answers, answers)
dispatcher.add_handler(answers_handler)


#-- News handler
# Unused in latest commit: Evaluate deletion
class News:
    title = 'A title'
    content = 'Text'
    date = datetime.date(1943,3,13)  #year, month, day
    #print(date.strftime("%A"))
    def __init__(self, title, content, date):
        self.title = title
        self.content = content
        self.date = date

# demo datas for news
news1 = News(title='News 1', content='Lorem ipsum dolor sit', date=datetime.date(2018,3,13))
news2 = News(title='News 2', content='Consectetur adipiscing elit', date=datetime.date(2018,12,25))
newsList = [news1, news2]

@send_typing_action
def fetch_news(bot, update):
    client = Client(url = 'https://hknpolito.org/xmlrpc', username = "HKNP0lit0", password = os.environ['HKN_WEB_PASSWORD'])
    postfilters = {"number": 3, "order": "ASC"}
    postsdict = client.call(posts.GetPosts(postfilters))
    #for theNews in newsList:
    #    bot.send_message(chat_id=update.message.chat_id, text=theNews.content)
    for post in postsdict:
        content = post.title + "\n" + post.link
        bot.send_message(chat_id=update.message.chat_id, text=content)


# Event handler
class Event:
    title = 'A title'
    description = 'Text'
    date = datetime.datetime(1943,3, 13) #year, month, day
    imageLink = str() #optional
    facebookLink = str() #optional
    eventbriteLink = str() #optional
    def __init__(self, title, description, date):
        self.title = title
        self.description = description
        self.date = date

# demo datas for events
event1 = Event(title='Event 1', description='Evento di marzo (passato)', date=datetime.datetime(2018,3,13))
event2 = Event(title='Event 2', description='Evento di dicembre', date=datetime.datetime(2018,12,25))
event2.imageLink = 'https://hknpolito.org/wp-content/uploads/2018/05/33227993_2066439693603577_8978955090240995328_o.jpg'
event2.facebookLink = 'https://www.google.it/webhp?hl=it'
event2.eventbriteLink = 'https://www.google.it/webhp?hl=it'
eventList = [event1, event2]

@send_typing_action
def fetch_events(bot, update):
    for theEvent in eventList:
        todayDate = datetime.datetime.now()
        if theEvent.date > todayDate: #do not print past events
            if not theEvent.imageLink: #if there isn't an image link
                bot.send_message(chat_id=update.message.chat_id, text=theEvent.description)
            else:
                #Build link buttons
                keyboard = []
                if  theEvent.facebookLink and theEvent.eventbriteLink:
                    keyboard = [[InlineKeyboardButton("Facebook Page", callback_data='1',url='https://www.google.it/webhp?hl=it'),
                        InlineKeyboardButton("Eventbrite", callback_data='2',url='https://www.google.it/webhp?hl=it')]]
                elif theEvent.facebookLink:
                    keyboard = [[InlineKeyboardButton("Facebook Page", callback_data='1',url='https://www.google.it/webhp?hl=it')]]
                elif theEvent.eventbriteLink:
                    keyboard = [InlineKeyboardButton("Eventbrite", callback_data='2',url='https://www.google.it/webhp?hl=it')]
                else: continue #skip the sending of the links
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_photo(chat_id=update.message.chat_id, caption=theEvent.description, photo=theEvent.imageLink, reply_markup=reply_markup)



filter_events = filters.FilterEvents()
events_handler = MessageHandler(filter_events, fetch_events)
dispatcher.add_handler(events_handler)

filter_news = filters.FilterNews()
news_handler = MessageHandler(filter_news, fetch_news)
dispatcher.add_handler(news_handler)

updater.start_polling()
