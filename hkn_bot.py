#########################################################################################################
### HKN Telegram Bot. This is the code for the official bot of the Mu Nu Chapter of IEEE Eta Kappa Nu ###
#########################################################################################################

import os
import telegram
import filters
from telegram.ext import Updater
# Handling commands and conversations
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
# Tutoring part imports
import re
import html2text
from urllib.request import urlopen
# Events - news import
import time
import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, Filters
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

from functools import wraps

LIST_OF_ADMINS = []
with open("admins.txt", "r") as admins_file:
    for line in admins_file:
        LIST_OF_ADMINS.append(int(line))

def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(bot, update, *args, **kwargs)
    return wrapped

# Uncomment for debug
#print(os.environ['HKN_BOT_TOKEN'])

# Retrieving bot token
updater = Updater(token = os.environ['HKN_BOT_TOKEN'])

dispatcher = updater.dispatcher

import tutor
# Save tutoring groups in file
tutor.tutoringFile()

# Start command handler
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Benvenuto nel bot ufficiale di Eta Kappa Nu Polito!")
    custom_keyboard = [['Events', 'News'], ['Study Groups', 'Questions'],["About HKN"]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text="Scegli una di queste opzioni:", reply_markup=reply_markup)
    
# About handler
@send_typing_action
def about(bot, update):
    in_file = open("about.txt", "r", encoding="utf-8")
    bot.send_message(chat_id=update.message.chat_id, text=in_file.read())
    in_file.close()


# Questions handler
TYPING = 1
@send_typing_action
def questions(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Fai una domanda al MuNu Chapter di Eta Kappa Nu")
    return TYPING

# Question appender to file
def answers(bot,update):
    out_file = open("questions.txt","a+")
    user_id = str(update.effective_user.id)
    out_file.write((str(update.message.from_user.username)+"-"+user_id+"-"+update.message.text).strip("\n")+"\n")
    out_file.close()
    bot.send_message(chat_id=update.message.chat_id, text="La tua domanda è stata registrata, ti risponderemo a breve")
    for admin in LIST_OF_ADMINS:
        bot.send_message(chat_id=admin, text="Nuova domanda da: "+str(update.message.from_user.username)+"\n-"+update.message.text+"\n")  
    return ConversationHandler.END    
    
# News handler
@send_typing_action
def fetch_news(bot, update):
    client = Client(url = 'https://hknpolito.org/xmlrpc', username = "HKNP0lit0", password = os.environ['HKN_WEB_PASSWORD'])
    postfilters = {"number": 3, "order": "ASC"}
    postsdict = client.call(posts.GetPosts(postfilters))
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

# Demo datas for events
event1 = Event(title='Event 1', description='Evento di marzo (passato)', date=datetime.datetime(2018,3,13))
event2 = Event(title='Event 2', description='Evento di dicembre', date=datetime.datetime(2019,12,25))
event2.imageLink = 'https://hknpolito.org/wp-content/uploads/2018/05/33227993_2066439693603577_8978955090240995328_o.jpg'
event2.facebookLink = 'https://www.google.it/webhp?hl=it'
event2.eventbriteLink = 'https://www.google.it/webhp?hl=it'
eventList = [event1, event2]

@send_typing_action
def fetch_events(bot, update):
    n = 0
    for theEvent in eventList:
        todayDate = datetime.datetime.now()
        if theEvent.date > todayDate: #do not print past events
            n = n + 1
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

    if n == 0:
        bot.send_message(chat_id=update.message.chat_id, text="There aren't events in program right now. Stay tuned to HKN world!")
# Restricted commands

# Reply to answers handler

# Setting up conversation handler to wait for user message
ANSWER = 1
def popquestion(option = "cancel"):
    question_file = open("questions.txt", "r+")
    questions = question_file.readlines()
    if questions == []:
        question_file.close()
        return None
    question_file.seek(0)
    for q in questions[1:]:
        question_file.write(q)
    question_file.truncate()
    if(option == "enqueue"):
        question_file.write(questions[0])
    question_file.close()
    return questions[0].split("-")

@restricted
def answerquestion(bot, update):
    question = popquestion()
    if question == None:
        bot.send_message(chat_id=update.message.chat_id, text="Formato file questions.txt non corretto")
        return ConversationHandler.END
    message = update.message.text 
    bot.send_message(chat_id=question[1], text="Ciao {} ecco la risposta alla tua domanda:\n{}".format(question[0],message))
    return ConversationHandler.END

@restricted
def deletequestion(bot, update):
    popquestion()
    bot.send_message(chat_id=update.message.chat_id, text="Domanda cancellata")
    return ConversationHandler.END

@restricted
def savequestion(bot, update):
    question_file = open("questions.txt","r")
    question = question_file.readline()
    saved_file = open("savedquestions.txt", "a")
    saved_file.write(question)
    question_file.close
    saved_file.close
    bot.send_message(chat_id=update.message.chat_id, text="Domanda salvata correttamente")
    return ANSWER

@restricted
def skip(bot,update):
    bot.send_message(chat_id=update.message.chat_id, text="Domanda non risposta")
    popquestion(option="enqueue")
    return ConversationHandler.END

@restricted
def cancel(bot, update):    
    bot.send_message(chat_id=update.message.chat_id, text="Conversazione cancellata")
    return ConversationHandler.END

@restricted
def reply(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Rispondi alla domanda: \n")
    question_file = open("questions.txt","r")
    question = question_file.readline()
    if(question == ""):
        bot.send_message(chat_id=update.message.chat_id, text="Non ci sono più domande a cui rispondere")
        return ConversationHandler.END
    bot.send_message(chat_id=update.message.chat_id, text=question)
    question_file.close()
    return ANSWER

@restricted
def showpending(bot, update):
    question_file = open("questions.txt", "r")
    questions = question_file.readlines()
    n = 0
    for q in questions:
        question = q.split("-")
        bot.send_message(chat_id=update.message.chat_id, text=(question[0] + " " + question[2]))
        n = n + 1
    if(n == 0):
        bot.send_message(chat_id=update.message.chat_id, text="Tutte le domande sono state risposte")
 
    

    
@restricted
def showsaved(bot, update):
    question_file = open("savedquestions.txt", "r")
    questions = question_file.readlines()
    n = 0
    for q in questions:
        question = q.split("-")
        bot.send_message(chat_id=update.message.chat_id, text=(question[0] + " " + question[2]))
        n = n + 1
    if(n == 0):
        bot.send_message(chat_id=update.message.chat_id, text="Nessuna domanda salvata")

# Configurating handlers
reply_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("reply", reply)],
    states={ANSWER: [MessageHandler(Filters.text, answerquestion),
                     CommandHandler("skip", skip),
                     CommandHandler("delete", deletequestion),
                     CommandHandler("save", savequestion)]
           },
    fallbacks=[CommandHandler("cancel", cancel)]
)

filter_questions = filters.FilterQuestions()
question_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("questions", questions),
                  MessageHandler(filter_questions, questions)],
    states={TYPING: [MessageHandler(Filters.text, answers)]
           },
    fallbacks=[CommandHandler("cancel", cancel)]
)
dispatcher.add_handler(reply_conv_handler)
dispatcher.add_handler(question_conv_handler)


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

pendingq_handler = CommandHandler("showpending", showpending)
dispatcher.add_handler(pendingq_handler)

savedq_handler = CommandHandler("showsaved", showsaved)
dispatcher.add_handler(savedq_handler)

filter_tutoring = filters.FilterTutoring()
tutoring_handler = MessageHandler(filter_tutoring, tutor.tutoring)
com_tutoring_handler = CommandHandler("studygroups", tutor.tutoring)
dispatcher.add_handler(com_tutoring_handler)
dispatcher.add_handler(tutoring_handler)

filter_events = filters.FilterEvents()
events_handler = MessageHandler(filter_events, fetch_events)
com_events_handler = CommandHandler("events", fetch_events)
dispatcher.add_handler(com_events_handler)
dispatcher.add_handler(events_handler)

filter_news = filters.FilterNews()
news_handler = MessageHandler(filter_news, fetch_news)
com_news_handler = CommandHandler("news", fetch_news)
dispatcher.add_handler(com_events_handler)
dispatcher.add_handler(news_handler)

filter_about = filters.FilterAbout()
about_handler = MessageHandler(filter_about, about)
com_about_handler = CommandHandler("about", about)
dispatcher.add_handler(about_handler)
dispatcher.add_handler(com_about_handler)

updater.start_polling()
updater.idle()
