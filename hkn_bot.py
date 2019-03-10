#########################################################################################################
### HKN Telegram Bot. This is the code for the official bot of the Mu Nu Chapter of IEEE Eta Kappa Nu ###
#########################################################################################################

# Imports
import os
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import filters
import json
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext import Filters
import re
import html2text
from urllib.request import urlopen
import time
import datetime
# Downloads from website every day study groups dates
import tutor
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts
from functools import wraps
from telegram import ChatAction
# Lang dictionaries
from lang import lang_en
from lang import lang_it

# Dictionary which stores language used by every user
users = {}

# Bot's typing action
def send_action(action):
    # Sends `action` while processing func command
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

# Language selection
def select_language(user_id):
    if users.get(user_id) == None or users.get(user_id) == "EN":
        return lang_en
    else:
        return lang_it

from functools import wraps

# Handling of restricted commands
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

# Retrieving bot token (saved as an env variable)
updater = Updater(token = os.environ['HKN_BOT_TOKEN'])
# Setting handlers dispatcher
dispatcher = updater.dispatcher

# Save tutoring groups in file
tutor.tutoringFile()

# Start command handler
def start(bot, update):
    lang = select_language(update.effective_user.id)
    inline_keyboard = [[InlineKeyboardButton(lang["lang:it"], callback_data="lang:it"),
                        InlineKeyboardButton(lang["lang:en"], callback_data="lang:en")]]
    inline_reply_markup = InlineKeyboardMarkup(inline_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=lang["welcome"], reply_markup=inline_reply_markup)
    custom_keyboard = [[lang["events"], lang["news"]], [lang["studygroups"], lang["askus"]],[lang["about"]]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=lang["ckchoose"], reply_markup=reply_markup)

# Updates start message if language is changed    
def update_start_message(bot, update, lang):
    bot.send_message(chat_id=update.message.chat_id, text=lang["welcome_up"])
    custom_keyboard = [[lang["events"], lang["news"]], [lang["studygroups"], lang["askus"]],[lang["about"]]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=lang["ckchoose"], reply_markup=reply_markup)

# Inline buttons handler
def inline_button(bot, update):
    query = update.callback_query
    if query.data == "back":
        bot.send_message(chat_id=query.message.chat_id, text="La tua richiesta di domanda è stata annullata")
        return ConversationHandler.END
    elif query.data == "lang:it":
        users[update.effective_user.id] = "IT"
        update_start_message(bot, query, lang_it)
    elif query.data == "lang:en":
        users[update.effective_user.id] = "EN"
        update_start_message(bot, query, lang_en)


# About handler
@send_typing_action
def about(bot, update):
    lang = select_language(update.effective_user.id)
    bot.send_message(chat_id=update.message.chat_id, text=lang["abouttext"])


# Questions handler
# TODO language selection
TYPING = 1
@send_typing_action
def questions(bot, update):
    keyboard = [[InlineKeyboardButton("⬅ Back", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=update.message.chat_id, text="Fai una domanda al MuNu Chapter di Eta Kappa Nu", reply_markup=reply_markup)
    return TYPING

# Question appender to file
# TODO language selection
def answers(bot,update):
    out_file = open("questions.txt", "a+", encoding="utf-8")
    user_id = str(update.effective_user.id)
    out_file.write((str(update.message.from_user.username)+"-"+user_id+"-"+update.message.text).strip("\n")+"\n")
    out_file.close()
    bot.send_message(chat_id=update.message.chat_id, text="La tua domanda è stata registrata, ti risponderemo a breve")
    for admin in LIST_OF_ADMINS:
        bot.send_message(chat_id=admin, text="Nuova domanda da: "+str(update.message.from_user.username)+"\n-"+update.message.text+"\n")  
    return ConversationHandler.END    
    
# News handler
# TODO language selection
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
    def __init__(self, title, description, date, imageLink=None, facebookLink=None, eventbriteLink=None):
        self.title = title
        self.description = description
        self.date = date
        self.imageLink = imageLink
        self.facebookLink = facebookLink
        self.eventbriteLink = eventbriteLink

# Loads events from json file
def load_events():
        eventList = []
        with open("events.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                for x in data:
                    e = Event(
                        title = x["Title"],
                        date = datetime.datetime.strptime(x["Datetime"], "%Y %m %d"),
                        description = x["Description"],
                        imageLink = x["Image Link"],
                        eventbriteLink = x["Eventbrite Link"],
                        facebookLink = x["Facebook Link"]
                    )
                    eventList.append(e)
        return eventList

# Displays scheduled events
@send_typing_action
def display_events(bot, update):
    n = 0
    eventList = load_events()
    for theEvent in eventList:
        todayDate = datetime.datetime.now()
        if theEvent.date > todayDate: #do not print past events
            n = n + 1
            if not theEvent.imageLink: #if there isn't an image link
                bot.send_message(chat_id=update.message.chat_id, parse_mode="markdown", text="*"+theEvent.title+"*\n\n"+theEvent.description)
            else:
                #Build link buttons
                keyboard = []
                if  theEvent.facebookLink and theEvent.eventbriteLink:
                    keyboard = [[InlineKeyboardButton("Facebook Page", callback_data='1',url=theEvent.facebookLink),
                        InlineKeyboardButton("Eventbrite", callback_data='2',url=theEvent.eventbriteLink)]]
                elif theEvent.facebookLink:
                    keyboard = [[InlineKeyboardButton("Facebook Page", callback_data='1',url=theEvent.facebookLink)]]
                elif theEvent.eventbriteLink:
                    keyboard = [InlineKeyboardButton("Eventbrite", callback_data='2',url=theEvent.eventbriteLink)]
                else: continue #skip the sending of the links
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_photo(chat_id=update.message.chat_id, parse_mode="markdown", caption="*"+theEvent.title+"*\n\n"+theEvent.description, photo=theEvent.imageLink, reply_markup=reply_markup)
    if n == 0:
        bot.send_message(chat_id=update.message.chat_id, text="There aren't events in program right now. Stay tuned to HKN world!")

# Restricted commands (can be executed only by users in admins.txt)

# Reply to answers handler

# Setting up conversation handler to wait for user message
ANSWER = 1
def pop_question(option = "cancel"):
    question_file = open("questions.txt", "r+", encoding="utf-8")
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
def answer_question(bot, update):
    question = pop_question()
    if question == None:
        bot.send_message(chat_id=update.message.chat_id, text="Formato file questions.txt non corretto")
        return ConversationHandler.END
    message = update.message.text 
    bot.send_message(chat_id=question[1], text="Ciao {} ecco la risposta alla tua domanda:\n{}".format(question[0],message))
    return ConversationHandler.END

@restricted
def delete_question(bot, update):
    pop_question()
    bot.send_message(chat_id=update.message.chat_id, text="Domanda cancellata")
    return ConversationHandler.END

@restricted
def save_question(bot, update):
    question_file = open("questions.txt", "r", encoding="utf-8")
    question = question_file.readline()
    saved_file = open("savedquestions.txt", "a", encoding="utf-8")
    saved_file.write(question)
    question_file.close
    saved_file.close
    bot.send_message(chat_id=update.message.chat_id, text="Domanda salvata correttamente")
    return ANSWER

@restricted
def skip(bot,update):
    bot.send_message(chat_id=update.message.chat_id, text="Domanda non risposta")
    pop_question(option="enqueue")
    return ConversationHandler.END

@restricted
def cancel(bot, update):    
    bot.send_message(chat_id=update.message.chat_id, text="Conversazione cancellata")
    return ConversationHandler.END

@restricted
def reply(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Rispondi alla domanda: \n")
    question_file = open("questions.txt", "r", encoding="utf-8")
    question = question_file.readline()
    if(question == ""):
        bot.send_message(chat_id=update.message.chat_id, text="Non ci sono più domande a cui rispondere")
        return ConversationHandler.END
    bot.send_message(chat_id=update.message.chat_id, text=question)
    question_file.close()
    return ANSWER

@restricted
def showpending(bot, update):
    question_file = open("questions.txt", "r", encoding="utf-8")
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
    question_file = open("savedquestions.txt", "r", encoding="utf-8")
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
    states={ANSWER: [MessageHandler(Filters.text, answer_question),
                     CommandHandler("skip", skip),
                     CommandHandler("delete", delete_question),
                     CommandHandler("save", save_question)]
           },
    fallbacks=[CommandHandler("cancel", cancel)]
)

filter_questions = filters.FilterQuestions()
question_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("questions", questions),
                  MessageHandler(filter_questions, questions)],
    states={TYPING: [MessageHandler(Filters.text, answers)]
           },
    fallbacks=[CommandHandler("cancel", cancel),
               CallbackQueryHandler(inline_button)]
)

# Adding handlers
dispatcher.add_handler(reply_conv_handler)
dispatcher.add_handler(question_conv_handler)

start_handler = CommandHandler("start", start)
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
events_handler = MessageHandler(filter_events, display_events)
com_events_handler = CommandHandler("events", display_events)
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

inline_button_handler = CallbackQueryHandler(inline_button)
dispatcher.add_handler(inline_button_handler)

updater.start_polling()
updater.idle()
