#########################################################################################################
### HKN Telegram Bot. This is the code for the official bot of the Mu Nu Chapter of IEEE Eta Kappa Nu ###
#########################################################################################################

# Imports
import os
import psycopg2
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
from enum import Enum
# Downloads from website every day study groups dates
import tutor
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts
from functools import wraps
from telegram import ChatAction
# Lang dictionaries
from lang import lang_en
from lang import lang_it
import binascii
from Crypto.Cipher import AES
from Crypto.Hash import SHA3_512
from Crypto.Util.Padding import pad, unpad
from psycopg2 import Error

# Dictionary which stores language used by every user
users = {}

# URL of Postgres db
DATABASE_URL = os.environ['DATABASE_URL']

# enumeration to handle different keyboard types
class KeyboardType(Enum):
    DEFAULT = 1
    LANGUAGE = 2
    BACK = 3
    NEWSLETTER_CONFIRM = 4
    NEWSLETTER_UNSUB = 5

# function to get different keyboard types
def getKeyboard(type, lang):
    if type == KeyboardType.LANGUAGE:
        inline_keyboard = [[InlineKeyboardButton(lang["lang:it"], callback_data="lang:it"), InlineKeyboardButton(lang["lang:en"], callback_data="lang:en")]]
        return InlineKeyboardMarkup(inline_keyboard)
    elif type == KeyboardType.BACK:
        inline_keyboard = [[InlineKeyboardButton(lang["back"], callback_data="back")]]
        return InlineKeyboardMarkup(inline_keyboard)
    elif type == KeyboardType.NEWSLETTER_CONFIRM:
        keyboard_confirm = [[InlineKeyboardButton(lang["newsletterConfirm"], callback_data="confirm")], [InlineKeyboardButton(lang["back"], callback_data="back")]]
        return InlineKeyboardMarkup(keyboard_confirm)
    elif type == KeyboardType.NEWSLETTER_UNSUB:
        keyboard_unsub = [[InlineKeyboardButton(lang["newsletterUnsubscribe"], callback_data="unsubscribe")]]
        return InlineKeyboardMarkup(keyboard_unsub)
    else:
        custom_keyboard = [[lang["events"], lang["news"]], [lang["studygroups"], lang["askus"]], [lang["newsletter"], lang["drive"]], [lang["about"], lang["contact"]]]
        return telegram.ReplyKeyboardMarkup(custom_keyboard)

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

# Decrypt admins file and set LIST_OF_ADMINS variable
def decrypt():
    fr = open("admins.txt", 'r')
    hashed_key = binascii.a2b_base64(fr.readline().encode())
    hkn_key = os.environ['HKN_BOT_CIPHERKEY']
    if len(hkn_key) < 16:
        key = pad(hkn_key.encode(), 16)
    elif len(hkn_key) > 16:
        key = hkn_key[:16].encode()
    else:
        key = hkn_key.encode()
    hk = SHA3_512.new(key).digest()
    if hk != hashed_key:
        print('Wrong key!')
    aes = AES.new(key, AES.MODE_ECB)
    for i in fr:
        LIST_OF_ADMINS.append(int(unpad(aes.decrypt(binascii.a2b_base64(i.encode())), 16).decode().strip()))
    fr.close()

# Handling of restricted commands
LIST_OF_ADMINS = []
decrypt()

def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}. This action will be reported.".format(user_id))
            return
        return func(bot, update, *args, **kwargs)
    return wrapped

# Retrieving bot token (saved as an env variable)
updater = Updater(token = os.environ['HKN_BOT_TOKEN']) # -> metterlo come variabile d'ambiente
# Setting handlers dispatcher
dispatcher = updater.dispatcher


# Save tutoring groups in file
tutor.tutoringFile()

# Start command handler
def start(bot, update):
    lang = select_language(update.effective_user.id)
    bot.send_message(chat_id=update.message.chat_id, text=lang["welcome"], reply_markup=getKeyboard(KeyboardType.LANGUAGE, lang))
    custom_keyboard = [[lang["events"], lang["news"]], [lang["studygroups"], lang["askus"]], [lang["newsletter"], lang["drive"]], [lang["about"], lang["contact"]]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)

# Updates start message if language is changed    
def update_start_message(bot, update, lang):
    bot.send_message(chat_id=update.message.chat_id, text=lang["welcome_up"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))

# Inline buttons handler
def inline_button(bot, update):
    lang = select_language(update.effective_user.id)
    query = update.callback_query
    if query.data == "back":
        bot.send_message(chat_id=query.message.chat_id, text=lang["questionAbort"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))
        return ConversationHandler.END
    elif query.data == "confirm":
        try:
            # connect to db
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM subscribed WHERE id = {};".format(str(query.message.chat_id)))
            record = cursor.fetchone()
            
            # id is already a subscriber
            while(record):
                bot.send_message(chat_id=query.message.chat_id, text=lang["alreadySubscribed"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))
                return ConversationHandler.END

            # id is a new subscriber!
            cursor.execute("INSERT INTO subscribed(id) VALUES({})".format(query.message.chat_id))
            bot.send_message(chat_id=query.message.chat_id, text=lang["newsletterSubscription"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))
            return ConversationHandler.END
        except (Exception, psycopg2.Error) as error :
            # Postgres automatically rollback the transaction
            print ("Error while connecting to PostgreSQL", error)
        finally:
            if(conn):
                cursor.close()
                conn.close()
                print("PostgreSQL connection is closed")
    elif query.data == "unsubscribe":
        try:
            # connect to db and execute query
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute("DELETE FROM subscribed WHERE id = {}".format(query.message.chat_id))
            bot.send_message(chat_id=query.message.chat_id, text=lang["newsletterUnsubscription"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))
            return ConversationHandler.END
            
        except (Exception, psycopg2.Error) as error :
            # Postgres automatically rollback the transaction
            print ("Error while connecting to PostgreSQL", error)
        finally:
            if(conn):
                cursor.close()
                conn.close()
                print("PostgreSQL connection is closed")
    elif query.data == "lang:it":
        users[update.effective_user.id] = "IT"
        tutor.users[update.effective_user.id] = "IT"
        update_start_message(bot, query, lang_it)
    elif query.data == "lang:en":
        users[update.effective_user.id] = "EN"
        tutor.users[update.effective_user.id] = "EN"
        update_start_message(bot, query, lang_en)

# About handler
@send_typing_action
def about(bot, update):
    lang = select_language(update.effective_user.id)
    bot.send_message(chat_id=update.message.chat_id, text=lang["abouttext"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))


# Questions handler
# TODO language selection
TYPING = 1
@send_typing_action
def questions(bot, update):
    lang = select_language(update.effective_user.id)
    bot.send_message(chat_id=update.message.chat_id, text=lang["askAQuestion"], reply_markup=getKeyboard(KeyboardType.BACK, lang))
    return TYPING

# Question appender to file
# TODO language selection
def answers(bot,update):
    lang = select_language(update.effective_user.id)
    out_file = open("questions.txt", "a+", encoding="utf-8")
    user_id = str(update.effective_user.id)
    out_file.write((str(update.message.from_user.username)+"-"+user_id+"-"+update.message.text).strip("\n")+"\n")
    out_file.close()
    bot.send_message(chat_id=update.message.chat_id, text=lang["questionSaved"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))
    for admin in LIST_OF_ADMINS:
        bot.send_message(chat_id=admin, text=lang["newQuestionFrom"]+str(update.message.from_user.username)+"\n-"+update.message.text+"\n", reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))  
    return ConversationHandler.END    
    
# News handler
# TODO language selection
@send_typing_action
def fetch_news(bot, update):
    lang = select_language(update.effective_user.id)
    client = Client(url = 'https://hknpolito.org/xmlrpc', username = "HKNP0lit0", password = os.environ['HKN_WEB_PASSWORD'])
    postfilters = {"number": 3, "order": "ASC"}
    postsdict = client.call(posts.GetPosts(postfilters))
    for post in postsdict:
        content = post.title + "\n" + post.link
        bot.send_message(chat_id=update.message.chat_id, text=content, reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))


# Event handler
class Event:
    title = 'A title'
    description = 'Text'
    date = datetime.datetime(1943,3, 13) #year, month, day
    imageLink = str() #optional
    facebookLink = str() #optional
    eventbriteLink = str() #optional
    instagramLink = str() #optional

    def __init__(self, title, description, date, imageLink=None, facebookLink=None, eventbriteLink=None, instagramLink=None):
        self.title = title
        self.description = description
        self.date = date
        self.imageLink = imageLink
        self.facebookLink = facebookLink
        self.eventbriteLink = eventbriteLink
        self.instagramLink = instagramLink

# Loads events from json file
def load_events(update):
    lang = select_language(update.effective_user.id)
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
                facebookLink = x["Facebook Link"],
                instagramLink = x["Instagram Link"]
            )
            if x["Lang"] == lang["Lang"]:
                eventList.append(e)
    return eventList

# Displays scheduled events
@send_typing_action
def display_events(bot, update):
    lang = select_language(update.effective_user.id)
    n = 0
    eventList = load_events(update)
    for theEvent in eventList:
        todayDate = datetime.datetime.now()
        if theEvent.date > todayDate: #do not print past events
            n = n + 1
            if not theEvent.imageLink: #if there isn't an image link
                bot.send_message(chat_id=update.message.chat_id, parse_mode="markdown", text="*"+theEvent.title+"*\n\n"+theEvent.description, reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))
            else:
                #Build link buttons
                keyboard = []
                if  theEvent.facebookLink != "" and theEvent.eventbriteLink != "":
                    keyboard = [[InlineKeyboardButton("Facebook Page", callback_data='1',url=theEvent.facebookLink),
                        InlineKeyboardButton("Eventbrite", callback_data='2',url=theEvent.eventbriteLink)]]
                elif theEvent.facebookLink != "":
                    keyboard = [[InlineKeyboardButton("Facebook Page", callback_data='1',url=theEvent.facebookLink)]]
                elif theEvent.eventbriteLink != "":
                    keyboard = [[InlineKeyboardButton("Eventbrite", callback_data='2',url=theEvent.eventbriteLink)]]
                elif theEvent.instagramLink != "":
                    keyboard = [[InlineKeyboardButton("Instagram Page", callback_data='3',url=theEvent.instagramLink)]]
                else: 
                    continue #skip the sending of the links
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_photo(chat_id=update.message.chat_id, parse_mode="markdown", caption="*"+theEvent.title+"*\n\n"+theEvent.description, photo=theEvent.imageLink, reply_markup=reply_markup)
    if n == 0:  
        bot.send_message(chat_id=update.message.chat_id, text=lang["noEvents"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))

@send_typing_action
def display_newsletterSubscription(bot, update):
    lang = select_language(update.effective_user.id)

    try:
        # connect to db
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM subscribed WHERE id = {};".format(str(update.message.chat_id)))
        record = cursor.fetchone()
        isSubscribed = 0

        # id is already subscribed
        while(record):
            isSubscribed = 1
            bot.send_message(chat_id=update.message.chat_id, text=lang["alreadySubscribed"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))
            break;

        # id wants to be subscribed
        if(isSubscribed == 0):    
            bot.send_message(chat_id=update.message.chat_id, text=lang["newsletterAreYouSure"], reply_markup=getKeyboard(KeyboardType.NEWSLETTER_CONFIRM, lang))
            
    except (Exception, psycopg2.Error) as error :
        # Postgres automatically rollback the transaction
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if(conn):
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")

# Drive handler		
@send_typing_action
def display_drive(bot, update):
    lang = select_language(update.effective_user.id)
    bot.send_message(chat_id=update.message.chat_id, parse_mode = "HTML", text=lang["drive_link"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))  
	
# Contact handler
@send_typing_action
def contact(bot, update):
    lang = select_language(update.effective_user.id)
    bot.send_message(chat_id=update.message.chat_id, text=lang["contacttext"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))
	

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
    lang = select_language(update.effective_user.id)
    question = pop_question()
    if question == None:
        bot.send_message(chat_id=update.message.chat_id, text="Formato file questions.txt non corretto", reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))
        return ConversationHandler.END
    message = update.message.text 
    bot.send_message(chat_id=question[1], text=lang["hello"] + " {} ".format(question[0]) + lang["yourAnswer"] + "\n{}".format(message), reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))
    return ConversationHandler.END

@restricted
def delete_question(bot, update):
    lang = select_language(update.effective_user.id)
    pop_question()
    bot.send_message(chat_id=update.message.chat_id, text=lang["questionDeleted"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))
    return ConversationHandler.END

@restricted
def save_question(bot, update):
    lang = select_language(update.effective_user.id)
    
    # get first question
    question_file = open("questions.txt", "r", encoding="utf-8")
    question = question_file.readline()
    question_file.close

    # write question in file 'savedquestions.txt', if question is not already present
    savedQuestion_file = open("savedquestions.txt", "r", encoding="utf-8")
    savedQuestions = savedQuestion_file.readlines()
    savedQuestion_file.close()
    found = False
    for line in savedQuestions:
        if str(question) in line:
            found = True
            bot.send_message(chat_id=update.message.chat_id, text=lang["questionAlreadySaved"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))

    if not found:
        savedQuestion_file = open("savedquestions.txt", "a", encoding="utf-8")
        savedQuestion_file.write(question)
        savedQuestion_file.close()
        bot.send_message(chat_id=update.message.chat_id, text=lang["questionSavedCorrectly"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))

    return ANSWER

@restricted
def skip(bot,update):
    lang = select_language(update.effective_user.id)
    bot.send_message(chat_id=update.message.chat_id, text=lang["questionNotAnswered"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))
    pop_question(option="enqueue")
    return ConversationHandler.END

@restricted
def cancel(bot, update):
    lang = select_language(update.effective_user.id)  
    bot.send_message(chat_id=update.message.chat_id, text=lang["conversationDeleted"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))
    return ConversationHandler.END

@restricted
def reply(bot, update):
    lang = select_language(update.effective_user.id)
    bot.send_message(chat_id=update.message.chat_id, text=lang["answerQuestion"] + " \n", reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))
    question_file = open("questions.txt", "r", encoding="utf-8")
    question = question_file.readline()
    if(question == ""):
        bot.send_message(chat_id=update.message.chat_id, text=lang["noQuestions"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))
        return ConversationHandler.END
    bot.send_message(chat_id=update.message.chat_id, text=question, reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))
    question_file.close()
    return ANSWER

@restricted
def showpending(bot, update):
    lang = select_language(update.effective_user.id)
    question_file = open("questions.txt", "r", encoding="utf-8")
    questions = question_file.readlines()
    n = 0
    for q in questions:
        question = q.split("-")
        bot.send_message(chat_id=update.message.chat_id, text=(question[0] + " " + question[2]), reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))
        n = n + 1
    if(n == 0):
        bot.send_message(chat_id=update.message.chat_id, text=lang["questionsAnswered"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))
     
@restricted
def sendNewsletter(bot, update):
    lang = select_language(update.effective_user.id)

    idList = []
    try:
        # connect to db
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM subscribed;")
        rows = cursor.fetchall()

        # add ids to the list 
        for row in rows:
            idList.append(row[0])

    except (Exception, psycopg2.Error) as error :
        # Postgres automatically rollback the transaction
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if(conn):
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")

    # send newsletter to all the subscribed users
    with open("newsletter.json", "r", encoding="utf-8") as f:
        data = json.load(f) 
        for x in data:
            if(lang == lang_en): 
                for userId in idList: 
                    bot.send_message(chat_id=userId, text=x['DescriptionENG'], reply_markup=getKeyboard(KeyboardType.NEWSLETTER_UNSUB, lang))
            else:
                for userId in idList: 
                    bot.send_message(chat_id=userId, text=x['DescriptionITA'], reply_markup=getKeyboard(KeyboardType.NEWSLETTER_UNSUB, lang))
        f.close()

@restricted 
def showsaved(bot, update):
    lang = select_language(update.effective_user.id)
    question_file = open("savedquestions.txt", "r", encoding="utf-8")
    questions = question_file.readlines()
    n = 0
    for q in questions:
        question = q.split("-")
        bot.send_message(chat_id=update.message.chat_id, text=(question[0] + " " + question[2]), reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))
        n = n + 1
    if(n == 0):
        bot.send_message(chat_id=update.message.chat_id, text=lang["noQuestionsSaved"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang))

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
               CallbackQueryHandler(inline_button)] #TODO: probably CallbackQueryHandler useless
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

newsletter_handler = CommandHandler("sendnewsletter", sendNewsletter)
dispatcher.add_handler(newsletter_handler)

filter_tutoring = filters.FilterTutoring()
tutoring_handler = MessageHandler(filter_tutoring, tutor.tutoring)
com_tutoring_handler = CommandHandler("studygroups", tutor.tutoring)
dispatcher.add_handler(com_tutoring_handler)
dispatcher.add_handler(tutoring_handler)

filter_events = filters.FilterEvents()
events_handler = MessageHandler(filter_events, display_events)
com_events_handler = CommandHandler("events", display_events)
dispatcher.add_handler(events_handler)
dispatcher.add_handler(com_events_handler)

filter_newsletter = filters.FilterNewsletter()
newsletter_handler = MessageHandler(filter_newsletter, display_newsletterSubscription)
com_newsletter_handler = CommandHandler("newsletter", display_newsletterSubscription)
dispatcher.add_handler(com_newsletter_handler)
dispatcher.add_handler(newsletter_handler)

filter_drive = filters.FilterDrive()
drive_handler = MessageHandler(filter_drive, display_drive);
com_drive_handler = CommandHandler("drive", display_drive)
dispatcher.add_handler(com_drive_handler)
dispatcher.add_handler(drive_handler)

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

filter_contact = filters.FilterContact()
contact_handler = MessageHandler(filter_contact, contact)
com_contact_handler = CommandHandler("contact", contact)
dispatcher.add_handler(contact_handler)
dispatcher.add_handler(com_contact_handler)

inline_button_handler = CallbackQueryHandler(inline_button)
dispatcher.add_handler(inline_button_handler)

updater.start_polling()
updater.idle()
