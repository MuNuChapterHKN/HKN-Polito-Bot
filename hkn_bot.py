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

# URL of Postgres db
DATABASE_URL = os.environ['DATABASE_URL']

# get users dictionary from db 
def getUsersLanguage():
    users_dict = {}
    try:
        # connect to db
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users;")
        record = cursor.fetchone()

        # for each row, add entry in dictionary 
        while record is not None:
            users_dict[str(record[0])] = str(record[1])
            record = cursor.fetchone()

    except (Exception, psycopg2.Error) as error :
        # Postgres automatically rollback the transaction
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if(conn):
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")
            return users_dict
			
# get members list from db 
def getMembersID():
    memb = []
    try:
        # connect to db
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members;")
        record = cursor.fetchone()

        # for each row, add entry in the list 
        while record is not None:
            memb.append(record[0])
            record = cursor.fetchone()

    except (Exception, psycopg2.Error) as error :
        # Postgres automatically rollback the transaction
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if(conn):
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")
            return memb

# Dictionary which stores language used by every user
users = getUsersLanguage()
# List containing all the ID's of all members
members_list = getMembersID()

# enumeration to handle different keyboard types
class KeyboardType(Enum):
    DEFAULT = 1
    LANGUAGE = 2
    BACK = 3
    NEWSLETTER_CONFIRM = 4
    NEWSLETTER_UNSUB = 5
    ABOUT = 6
    DRIVE = 7
    MEMBERS = 8
    GROUPS = 9
    ELECTRONICENGINEERINGGROUPS = 10

# function to get different keyboard types
def getKeyboard(type, lang, user_id):
    if type == KeyboardType.BACK:
        inline_keyboard = [[InlineKeyboardButton(lang["back"], callback_data="back")]]
        return InlineKeyboardMarkup(inline_keyboard)
    elif type == KeyboardType.NEWSLETTER_CONFIRM:
        keyboard_confirm = [[InlineKeyboardButton(lang["newsletterConfirm"], callback_data="confirm")], [InlineKeyboardButton(lang["back"], callback_data="back")]]
        return InlineKeyboardMarkup(keyboard_confirm)
    elif type == KeyboardType.NEWSLETTER_UNSUB:
        keyboard_unsub = [[InlineKeyboardButton(lang["newsletterUnsubscribe"], callback_data="unsubscribe")]]
        return InlineKeyboardMarkup(keyboard_unsub)
    elif type == KeyboardType.LANGUAGE:
        start_keyboard = [[lang["lang_ita"],lang["lang_eng"]]]
        return telegram.ReplyKeyboardMarkup(start_keyboard, resize_keyboard=True)
    elif type == KeyboardType.ABOUT:
        inline_keyboard = [[InlineKeyboardButton(lang["website"], url="< LINK >")], [InlineKeyboardButton(lang["facebook"], url="< LINK >")], [InlineKeyboardButton(lang["instagram"], url="< LINK >")], [InlineKeyboardButton(lang["youtube"], url="< LINK >")]]
        return InlineKeyboardMarkup(inline_keyboard)
    elif type == KeyboardType.DRIVE:
        inline_keyboard = [[InlineKeyboardButton(lang["driveButton"], url="< LINK >")]]
        return InlineKeyboardMarkup(inline_keyboard)
    elif type == KeyboardType.MEMBERS:
	    #if the user is one of the members show the special buttons
        if user_id in members_list:
            inline_keyboard = [[InlineKeyboardButton(lang["FI"], url="< FI LINK >")],[InlineKeyboardButton(lang["TelegramGroups"], callback_data="TelegramGroups")], [InlineKeyboardButton(lang["HRGame"], callback_data="HRGame")]]	
            return InlineKeyboardMarkup(inline_keyboard)	
    elif type == KeyboardType.GROUPS:
        inline_keyboard = [[InlineKeyboardButton("EtaKazzateNu", url="< ETAKAZZATENU LINK >")], [InlineKeyboardButton("HKN Drive", url="< DRIVE LINK >")], [InlineKeyboardButton("HKN-Polito Discord Server", url="< DISCORD SERVER LINK >")], [InlineKeyboardButton("HKGirls", url="< HKGIRLS LINK >")], [InlineKeyboardButton("Eta PN junction NU", url="< ETA PN JUNCTION NU LINK >")], [InlineKeyboardButton("Eta Kappa PhD", url="< ETA KAPPA PHD LINK >")], [InlineKeyboardButton("hknMUsicNUChapter", url="< HKN MUSIC LINK >")],  [InlineKeyboardButton("BiblioteKappaNu", url="< BIBLIOTAKAPPANU LINK >")], [InlineKeyboardButton("EtaKappaNerds", url="< ETAKAPPANERDS LINK >")], [InlineKeyboardButton("HKRocket League", url="< HKROCKET LEAGUE LINK >")], [InlineKeyboardButton("EtaKappaMovies", url="< ETAKAPPAMOVIES LINK >")], [InlineKeyboardButton("EtaKappaSports", url="< ETAKAPPASPORTS LINK >")], [InlineKeyboardButton("EtaKoseaMuzzo", url="< ETAKOSEAMUZZO LINK >")], [InlineKeyboardButton("EtanoloKappaNu", url="< ETANOLOKAPPANU LINK >")], [InlineKeyboardButton("Eta Kidding Nu", url="< ETAMEMENU LINK >")], [InlineKeyboardButton("HKN x gif", url="< HKN x GIF LINK >")]]
        return InlineKeyboardMarkup(inline_keyboard)
    else:
		#if the user is one of the members show the members keyboard
        if user_id in members_list:
            custom_keyboard = [[lang["events"], lang["news"]], [lang["studygroups"], lang["askus"]], [lang["newsletter"], lang["drive"]], [lang["about"], lang["contact"]], [lang["members"], lang["electronicengineeringgroups"]]]
        else:
            custom_keyboard = [[lang["events"], lang["news"]], [lang["studygroups"], lang["askus"]], [lang["newsletter"], lang["drive"]], [lang["about"], lang["contact"]],  [lang["electronicengineeringgroups"]]]
        return telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)

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
    if users.get(str(user_id)) == None or users.get(str(user_id)) == "EN":
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
tutor.users = users
tutor.tutoringFile()

# Start command handler
def start(bot, update):
    lang = select_language(update.effective_user.id)
    user_id = update.effective_user.id
    bot.send_message(chat_id=update.message.chat_id, text=lang["welcome"], reply_markup=getKeyboard(KeyboardType.LANGUAGE, lang, user_id))
	
# Help command handler
def help(bot, update):
    lang = select_language(update.effective_user.id)
    bot.send_message(chat_id=update.message.chat_id, text=lang["welcome_up"])


# Updates start message if language is changed    
def update_start_message(bot, update, lang):
    user_id = update.effective_user.id
    bot.send_message(chat_id=update.message.chat_id, text=lang["welcome_up"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))

# Inline buttons handler
def inline_button(bot, update):
    lang = select_language(update.effective_user.id)
    query = update.callback_query
    user_id = update.effective_user.id
    if query.data == "back":
        bot.send_message(chat_id=query.message.chat_id, text=lang["questionAbort"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))
        return ConversationHandler.END
    elif query.data =="Triennale":
        bot.send_message(chat_id=query.message.chat_id, parse_mode='HTML', text='ðŸŽ“ English Course:  \n - <a href="< LINK >">Communication networks</a> \n - <a href="< LINK >">Electronic devices</a> \n - <a href="< LINK >">Automatic control</a> \n - <a href="< LINK >">Electronic Circuits</a> \n - <a href="< LINK >">Applied electronics</a> \n - <a href="< LINK >">Digital transmission</a> \n - <a href="< LINK >">Electromagnetic waves and antennas</a> \n - <a href="< LINK >">Applied signal processing laboratory</a> \n - <a href="< LINK >">Digital systems electronics</a> \n - <a href="< LINK >">Electronic measurements</a> \n \n \n ðŸŽ“ Corso Italiano:  \n - <a href="< LINK >">Economia urbana</a> \n - <a href="< LINK >">Misure</a> \n - <a href="< LINK >">Fibre: preparazione, proprietÃ  e tecnologie di trasformazione</a> \n - <a href="< LINK >">Ingegneria delle cellule e dei tessuti</a> \n - <a href="< LINK >">Ingegneria nelle terapie medico-chirurgiche</a> \n - <a href="< LINK >">RSelezione e progettazione dei materiali per applicazioni ingegneristiche (SPMAI)</a> \n - <a href="< LINK >">Architettura tecnica e cultura del costruito</a> \n - <a href="< LINK >">Strumenti e metodi per la sostenibilitÃ  dei sistemi edilizi e territoriali</a> \n - <a href="< LINK >">Electromagnetic fields</a> \n - <a href="< LINK >">Processi dell industria alimentare</a>\n - <a href="< LINK >">Valutazioni di impatto ambientale</a> \n - <a href="< LINK >">Electronic measurements</a> \n - <a href="< LINK >">Teoria dei segnali e delle comunicazioni</a> \n - <a href="< LINK >">Electronic Circuits</a> \n - <a href="< LINK >">Digital systems electronics</a> \n - <a href="< LINK >">Campi elettromagnetici</a> \n - <a href="< LINK >">Electronic devices</a> \n - <a href="< LINK >">Elettronica dei sistemi digitali</a> \n - <a href="< LINK >">Dispositivi elettronici</a> \n - <a href="< LINK >">Circuiti elettronici</a> \n - <a href="< LINK >">Analisi matematica II</a> \n - <a href="< LINK >">Fisica II</a> \n - <a href="< LINK >">Metodi matematici per l ingegneria</a> \n - <a href="< LINK >">Elettrotecnica</a>')
        return ConversationHandler.END
    elif query.data =="Magistrale":
        bot.send_message(chat_id=query.message.chat_id, parse_mode='HTML', text='ðŸŽ“ Master:  \n - <a href="< LINK >">Sistemi digitali integrati</a> \n - <a href="< LINK >">Testing and certification</a> \n - <a href="< LINK >">High speed electron devices</a> \n - <a href="< LINK >">Finite element modelling</a> \n - <a href="< LINK >">Elettronica analogica e di potenza</a> \n - <a href="< LINK >">Radar and remote sensing</a> \n - <a href="< LINK >">Microwave electronics</a> \n - <a href="< LINK >">Sistemi elettronici a basso consumo</a> \n - <a href="< LINK >">Electronic systems engineering</a> \n - <a href="< LINK >">Integrated systems technology</a>\n - <a href="< LINK >">Photonic devices</a> \n - <a href="< LINK >">Microelectronic systems</a> \n - <a href="< LINK >">Communication systems</a> \n - <a href="< LINK >">Analog and telecommunication electronics</a> \n - <a href="< LINK >">Radiating electromagnetic systems</a> \n - <a href="< LINK >">Guiding electromagnetic systems</a> \n - <a href="< LINK >">Sistemi di misura e sensori</a> \n - <a href="< LINK >">Microelettronica digitale</a> \n - <a href="< LINK >">Advanced antenna engineering</a> \n - <a href="< LINK >">Microelettronica digitale</a> \n - <a href="< LINK >">Computer aided design of communication systems</a> \n - <a href="< LINK >">Mobile and sensor networks</a> \n - <a href="< LINK >">Electronics for embedded systems</a> \n - <a href="< LINK >">Modeling and optimization of embedded systems</a> \n - <a href="< LINK >">Codesign methods and tools</a> \n - <a href="< LINK >">Convex optimization and engineering applications</a> \n - <a href="< LINK >">Electromagnetic fields and biological tissues: effects and medical applications</a>\n- <a href="< LINK >">Innovative wireless platforms for the internet of things</a> \n - <a href="< LINK >">Bioinformatics</a> \n - <a href="< LINK >">Automation and planning of production systems</a> \n - <a href="< LINK >">Advanced electronic drives</a> \n - <a href="< LINK >">Radio frequency integrated circuits</a> \n - <a href="< LINK >">Analog integrated circuits</a> \n - <a href="< LINK >">Projects and laboratory on communication systems</a> \n - <a href="< LINK >">Big data: architectures and data analytics</a> \n - <a href="< LINK >">Testing and fault tolerance</a>\n - <a href="< LINK >">Nanomaterials and nanotechnologies for energy applications</a> \n - <a href="< LINK >">Integrazione di sistemi embedded</a> \n - <a href="< LINK >">Industrial Photonics</a> \n - <a href="< LINK >">Open Optical Networks</a> \n - <a href="< LINK >">Signal Processing and Wireless Transmission Lab</a> \n - <a href="< LINK >">Signal Processing and Optical Transmission Lab</a> \n - <a href="< LINK >">Engineering Empathy</a>\n - <a href="< LINK >">Micro and Nanoelectronic Devices</a> \n - <a href="< LINK >">CAD of semiconductor devices</a> \n - <a href="< LINK >">Electronic transport in crystalline and organic semiconductors</a> \n - <a href="< LINK >">Nanoelectronic systems</a> \n - <a href="< LINK >">Microelectronics and Micro/Nanosystems Technologies</a> \n - <a href="< LINK >">Introduction to MEMS and Bio-MEMS</a> \n - <a href="< LINK >">Design of microsystems</a> \n - <a href="< LINK >">Wireless Integrated Circuits and Systems</a> \n - <a href="< LINK >">Integrated systems architecture</a> \n - <a href="< LINK >">Power electronics</a> \n - <a href="< LINK >">Computer architectures</a> \n - <a href="< LINK >">Synthesis and optimization of digital systems</a> \n - <a href="< LINK >">Digital Electronics</a> \n - <a href="< LINK >">Passive Optical Components</a> \n - <a href="< LINK >">Advanced design for signal integrity and compliance</a> \n - <a href="< LINK >">Tecnologie digitali e societÃ </a> \n - <a href="< LINK >">Sistemi robotici</a> \n - <a href="< LINK >">Digital Communications</a>\n - <a href="< LINK >">Operating systems</a> \n - <a href="< LINK >">Optoelettronica</a>')        
        return ConversationHandler.END
    elif query.data == "HRGame":
        inline_keyboard = [[InlineKeyboardButton(lang["Classifica"], url="<RANKING LINK>")]]
        bot.send_message(chat_id=query.message.chat_id, text=lang["HRRes"], reply_markup=InlineKeyboardMarkup(inline_keyboard))
        return ConversationHandler.END
    elif query.data == "TelegramGroups":
        bot.send_message(chat_id=query.message.chat_id, text=lang["GroupsText"], reply_markup=getKeyboard(KeyboardType.GROUPS, lang, user_id))
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
                bot.send_message(chat_id=query.message.chat_id, text=lang["alreadySubscribed"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))
                return ConversationHandler.END

            # id is a new subscriber!
            cursor.execute("INSERT INTO subscribed(id) VALUES({})".format(query.message.chat_id))
            bot.send_message(chat_id=query.message.chat_id, text=lang["newsletterSubscription"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))
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
            bot.send_message(chat_id=query.message.chat_id, text=lang["newsletterUnsubscription"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))
            return ConversationHandler.END
            
        except (Exception, psycopg2.Error) as error :
            # Postgres automatically rollback the transaction
            print ("Error while connecting to PostgreSQL", error)
        finally:
            if(conn):
                cursor.close()
                conn.close()
                print("PostgreSQL connection is closed")

# About handler
@send_typing_action
def about(bot, update):
    lang = select_language(update.effective_user.id)
    user_id = update.effective_user.id
    bot.send_message(chat_id=update.message.chat_id, text=lang["abouttext"], reply_markup=getKeyboard(KeyboardType.ABOUT, lang, user_id))

# Selection of the language it
def sel_language_ita(bot, update):
    lang = "IT"
    updateUserLanguage(str(update.effective_user.id), lang)
    users[str(update.effective_user.id)] = lang
    tutor.users[str(update.effective_user.id)] = lang
    update_start_message(bot, update, lang_it)

# Selection of the language en
def sel_language_eng(bot, update):
    lang = "EN"
    updateUserLanguage(str(update.effective_user.id), lang)
    users[str(update.effective_user.id)] = lang
    tutor.users[str(update.effective_user.id)] = lang
    update_start_message(bot, update, lang_en)

# Insert or update user language in db
def updateUserLanguage(user_id, language):
    try:
        # connect to db
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT lang FROM users WHERE id = '{}';".format(user_id))
        record = cursor.fetchone()
        updated = False

        # user exists, update its language 
        while record:
            if language not in record:
                cursor.execute("UPDATE users SET lang = '{}' WHERE id = '{}';".format(language, user_id))
            updated = True
            break

        # user not exists, insert it with selected language
        if not updated:
            cursor.execute("INSERT INTO users(id, lang) VALUES('{}', '{}')".format(user_id, language))
    except (Exception, psycopg2.Error) as error :
        # Postgres automatically rollback the transaction
        print ("Error while connecting to PostgreSQL", error)
    finally:
        if(conn):
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")

# Questions handler
# TODO language selection
TYPING = 1
@send_typing_action
def questions(bot, update):
    lang = select_language(update.effective_user.id)
    user_id = update.effective_user.id
    bot.send_message(chat_id=update.message.chat_id, text=lang["askAQuestion"], reply_markup=getKeyboard(KeyboardType.BACK, lang, user_id))
    return TYPING

# Question appender to file
# TODO language selection
def answers(bot,update):
    lang = select_language(update.effective_user.id)
    out_file = open("questions.txt", "a+", encoding="utf-8")
    user_id = str(update.effective_user.id)
    user_id1 = update.effective_user.id
    out_file.write((str(update.message.from_user.username)+"-"+user_id+"-"+update.message.text).strip("\n")+"\n")
    out_file.close()
    bot.send_message(chat_id=update.message.chat_id, text=lang["questionSaved"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id1))
    for admin in LIST_OF_ADMINS:
        bot.send_message(chat_id=admin, text=lang["newQuestionFrom"]+str(update.message.from_user.username)+"\n-"+update.message.text+"\n", reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))  
    return ConversationHandler.END    
    
# News handler
# TODO language selection
@send_typing_action
def fetch_news(bot, update):
    lang = select_language(update.effective_user.id)
    client = Client(url = 'https://hknpolito.org/xmlrpc', username = "< HKN USERNAME >", password = os.environ['HKN_WEB_PASSWORD'])
    postfilters = {"number": 3, "order": "ASC"}
    postsdict = client.call(posts.GetPosts(postfilters))
    user_id = update.effective_user.id
    for post in postsdict:
        content = post.title + "\n" + post.link
        bot.send_message(chat_id=update.message.chat_id, text=content, reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))


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
    user_id = update.effective_user.id
    for theEvent in eventList:
        todayDate = datetime.datetime.now()
        if theEvent.date > todayDate: #do not print past events
            n = n + 1
            if not theEvent.imageLink: #if there isn't an image link
                bot.send_message(chat_id=update.message.chat_id, parse_mode="markdown", text="*"+theEvent.title+"*\n\n"+theEvent.description, reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))
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
        bot.send_message(chat_id=update.message.chat_id, text=lang["noEvents"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))

@send_typing_action
def display_newsletterSubscription(bot, update):
    lang = select_language(update.effective_user.id)
    user_id = update.effective_user.id

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
            bot.send_message(chat_id=update.message.chat_id, text=lang["alreadySubscribed"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))
            break;

        # id wants to be subscribed
        if(isSubscribed == 0):    
            bot.send_message(chat_id=update.message.chat_id, text=lang["newsletterAreYouSure"], reply_markup=getKeyboard(KeyboardType.NEWSLETTER_CONFIRM, lang, user_id))
            
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
    user_id = update.effective_user.id
    bot.send_message(chat_id=update.message.chat_id, text=lang["drivetext"], reply_markup=getKeyboard(KeyboardType.DRIVE, lang, user_id))   
	
# Contact handler
@send_typing_action
def contact(bot, update):
    lang = select_language(update.effective_user.id)
    user_id = update.effective_user.id
    bot.send_message(chat_id=update.message.chat_id, text=lang["contacttext"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))
	
# Members handler
@send_typing_action
def members(bot, update):
    lang = select_language(update.effective_user.id)
    user_id = update.effective_user.id
    bot.send_message(chat_id=update.message.chat_id, text=lang["memberstext"], reply_markup=getKeyboard(KeyboardType.MEMBERS, lang, user_id))	

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
    user_id = update.effective_user.id
    if question == None:
        bot.send_message(chat_id=update.message.chat_id, text="Formato file questions.txt non corretto", reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))
        return ConversationHandler.END
    message = update.message.text 
    bot.send_message(chat_id=question[1], text=lang["hello"] + " {} ".format(question[0]) + lang["yourAnswer"] + "\n{}".format(message), reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))
    return ConversationHandler.END

@restricted
def delete_question(bot, update):
    lang = select_language(update.effective_user.id)
    pop_question()
    user_id = update.effective_user.id
    bot.send_message(chat_id=update.message.chat_id, text=lang["questionDeleted"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))
    return ConversationHandler.END

@restricted
def save_question(bot, update):
    lang = select_language(update.effective_user.id)
    user_id = update.effective_user.id
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
            bot.send_message(chat_id=update.message.chat_id, text=lang["questionAlreadySaved"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))

    if not found:
        savedQuestion_file = open("savedquestions.txt", "a", encoding="utf-8")
        savedQuestion_file.write(question)
        savedQuestion_file.close()
        bot.send_message(chat_id=update.message.chat_id, text=lang["questionSavedCorrectly"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))

    return ANSWER

@restricted
def skip(bot,update):
    lang = select_language(update.effective_user.id)
    user_id = update.effective_user.id
    bot.send_message(chat_id=update.message.chat_id, text=lang["questionNotAnswered"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))
    pop_question(option="enqueue")
    return ConversationHandler.END

@restricted
def cancel(bot, update):
    lang = select_language(update.effective_user.id)  
    user_id = update.effective_user.id
    bot.send_message(chat_id=update.message.chat_id, text=lang["conversationDeleted"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))
    return ConversationHandler.END

@restricted
def reply(bot, update):
    lang = select_language(update.effective_user.id)
    user_id = update.effective_user.id
    bot.send_message(chat_id=update.message.chat_id, text=lang["answerQuestion"] + " \n", reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))
    question_file = open("questions.txt", "r", encoding="utf-8")
    question = question_file.readline()
    if(question == ""):
        bot.send_message(chat_id=update.message.chat_id, text=lang["noQuestions"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))
        return ConversationHandler.END
    bot.send_message(chat_id=update.message.chat_id, text=question, reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))
    question_file.close()
    return ANSWER

@restricted
def showpending(bot, update):
    lang = select_language(update.effective_user.id)
    user_id = update.effective_user.id
    question_file = open("questions.txt", "r", encoding="utf-8")
    questions = question_file.readlines()
    n = 0
    for q in questions:
        question = q.split("-")
        bot.send_message(chat_id=update.message.chat_id, text=(question[0] + " " + question[2]), reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))
        n = n + 1
    if(n == 0):
        bot.send_message(chat_id=update.message.chat_id, text=lang["questionsAnswered"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))
     
@restricted
def sendNewsletter(bot, update):
    lang = select_language(update.effective_user.id)
    user_id = update.effective_user.id

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
                    bot.send_message(chat_id=userId, text=x['DescriptionENG'], reply_markup=getKeyboard(KeyboardType.NEWSLETTER_UNSUB, lang, user_id))
            else:
                for userId in idList: 
                    bot.send_message(chat_id=userId, text=x['DescriptionITA'], reply_markup=getKeyboard(KeyboardType.NEWSLETTER_UNSUB, lang, user_id))
        f.close()

@restricted 
def showsaved(bot, update):
    lang = select_language(update.effective_user.id)
    question_file = open("savedquestions.txt", "r", encoding="utf-8")
    questions = question_file.readlines()
    user_id = update.effective_user.id

    n = 0
    for q in questions:
        question = q.split("-")
        bot.send_message(chat_id=update.message.chat_id, text=(question[0] + " " + question[2]), reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))
        n = n + 1
    if(n == 0):
        bot.send_message(chat_id=update.message.chat_id, text=lang["noQuestionsSaved"], reply_markup=getKeyboard(KeyboardType.DEFAULT, lang, user_id))

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

help_handler = CommandHandler("help", help)
dispatcher.add_handler(help_handler)

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

filter_members = filters.FilterMembers()
members_handler = MessageHandler(filter_members, members)
com_members_handler = CommandHandler("members", members)
dispatcher.add_handler(members_handler)
dispatcher.add_handler(com_members_handler)

filter_it = filters.FilterIt()
it_handler = MessageHandler(filter_it, sel_language_ita);
com_it_handler = CommandHandler("lang_ita", sel_language_ita)
dispatcher.add_handler(com_it_handler)
dispatcher.add_handler(it_handler)

filter_en = filters.FilterEn()
en_handler = MessageHandler(filter_en, sel_language_eng);
com_en_handler = CommandHandler("lang_eng", sel_language_eng)
dispatcher.add_handler(com_en_handler)
dispatcher.add_handler(en_handler)

inline_button_handler = CallbackQueryHandler(inline_button)
dispatcher.add_handler(inline_button_handler)

updater.start_polling()
updater.idle()
