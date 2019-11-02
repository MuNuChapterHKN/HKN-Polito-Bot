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

# Retrieving bot token (saved as an env variable)
updater = Updater(token = os.environ['HKN_BOT_TOKEN']) # -> metterlo come variabile d'ambiente
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
    custom_keyboard = [[lang["events"], lang["news"]], [lang["studygroups"], lang["askus"]],[lang["about"]], [lang["newsletter"]]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=lang["ckchoose"], reply_markup=reply_markup)

# Updates start message if language is changed    
def update_start_message(bot, update, lang):
    bot.send_message(chat_id=update.message.chat_id, text=lang["welcome_up"])
    custom_keyboard = [[lang["events"], lang["news"]], [lang["studygroups"], lang["askus"]],[lang["about"]], [lang["newsletter"]]]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=lang["ckchoose"], reply_markup=reply_markup)

# Inline buttons handler
def inline_button(bot, update):
    lang = select_language(update.effective_user.id)
    query = update.callback_query
    if query.data == "back":
        bot.send_message(chat_id=query.message.chat_id, text=lang["questionAbort"])
        return ConversationHandler.END
    elif query.data == "confirm":
        subscriber = {"id": query.message.chat_id} # new subscriber!
        with open('userIDs.json') as f: # open file to read the list of IDs
            idList = json.load(f)
        with open("userIDs.json", mode='w', encoding='utf-8') as data:
            #TODO: check if it is already present 
            idList.append(subscriber) # add new subscriber to current list
            json.dump(idList, data)
        f.close()
        data.close()
        bot.send_message(chat_id=query.message.chat_id, text=lang["newsletterSubscription"])
        return ConversationHandler.END
    elif query.data == "unsubscribe":
        subscriber = {"id": query.message.chat_id} # subscriber to remove
        with open('userIDs.json', 'r') as data_file:
            idList = json.load(data_file)
        res = [i for i in idList if not (i['id'] == subscriber['id'])]  # return new dict without that subscriber
        with open('userIDs.json', 'w') as data_file:
            json.dump(res, data_file)
        data_file.close()
        bot.send_message(chat_id=query.message.chat_id, text=lang["newsletterUnsubscription"])
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
    lang = select_language(update.effective_user.id)
    keyboard = [[InlineKeyboardButton(lang["back"], callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.send_message(chat_id=update.message.chat_id, text=lang["askAQuestion"], reply_markup=reply_markup)
    return TYPING

# Question appender to file
# TODO language selection
def answers(bot,update):
    lang = select_language(update.effective_user.id)
    out_file = open("questions.txt", "a+", encoding="utf-8")
    user_id = str(update.effective_user.id)
    out_file.write((str(update.message.from_user.username)+"-"+user_id+"-"+update.message.text).strip("\n")+"\n")
    out_file.close()
    bot.send_message(chat_id=update.message.chat_id, text=lang["questionSaved"])
    for admin in LIST_OF_ADMINS:
        bot.send_message(chat_id=admin, text=lang["newQuestionFrom"]+str(update.message.from_user.username)+"\n-"+update.message.text+"\n")  
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
                bot.send_message(chat_id=update.message.chat_id, parse_mode="markdown", text="*"+theEvent.title+"*\n\n"+theEvent.description)
            else:
                #Build link buttons
                keyboard = []
                if  theEvent.facebookLink != "" and theEvent.eventbriteLink != "":
                    print("entrato1")
                    keyboard = [[InlineKeyboardButton("Facebook Page", callback_data='1',url=theEvent.facebookLink),
                        InlineKeyboardButton("Eventbrite", callback_data='2',url=theEvent.eventbriteLink)]]
                elif theEvent.facebookLink != "":
                    print("entrato2")
                    keyboard = [[InlineKeyboardButton("Facebook Page", callback_data='1',url=theEvent.facebookLink)]]
                elif theEvent.eventbriteLink != "":
                    print("entrato3")
                    keyboard = [InlineKeyboardButton("Eventbrite", callback_data='2',url=theEvent.eventbriteLink)]
                elif theEvent.instagramLink != "":
                    print("entrato4")
                    keyboard = [InlineKeyboardButton("Instagram Page", callback_data='3',url=theEvent.instagramLink)]
                else: 
                    print("entrato5")
                    continue #skip the sending of the links
                reply_markup = InlineKeyboardMarkup(keyboard)
                bot.send_photo(chat_id=update.message.chat_id, parse_mode="markdown", caption="*"+theEvent.title+"*\n\n"+theEvent.description, photo="https://hknpolito.org/wp-content/uploads/2019/03/LikeAtHomeLocandina_2160x1080.png", reply_markup=reply_markup)
    if n == 0:  
        bot.send_message(chat_id=update.message.chat_id, text=lang["noEvents"])

@send_typing_action
def display_newsletterSubscription(bot, update):
    lang = select_language(update.effective_user.id)
    keyboard_confirm = [[InlineKeyboardButton(lang["newsletterConfirm"], callback_data="confirm")], 
                        [InlineKeyboardButton(lang["back"], callback_data="back")]]
    reply_markup_confirm = InlineKeyboardMarkup(keyboard_confirm)
    subscriber = {"id": update.message.chat_id} # new subscriber!
    if(os.stat("userIDs.json").st_size == 0): # if file is empty
        file = open("userIDs.json","w") 
        file.write("[]") 
        file.close()
    with open('userIDs.json') as f: # open file to read the list of IDs
        idList = json.load(f)
    if re.search('"id": {}'.format(subscriber['id']), json.dumps(idList), re.M): # this ID is already subscribed
        bot.send_message(chat_id=update.message.chat_id, text=lang["alreadySubscribed"])
        f.close()
    else :
        bot.send_message(chat_id=update.message.chat_id, text=lang["newsletterAreYouSure"], reply_markup=reply_markup_confirm)

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
        bot.send_message(chat_id=update.message.chat_id, text="Formato file questions.txt non corretto")
        return ConversationHandler.END
    message = update.message.text 
    bot.send_message(chat_id=question[1], text=lang["hello"] + " {} ".format(question[0]) + lang["yourAnswer"] + "\n{}".format(message))
    return ConversationHandler.END

@restricted
def delete_question(bot, update):
    lang = select_language(update.effective_user.id)
    pop_question()
    bot.send_message(chat_id=update.message.chat_id, text=lang["questionDeleted"])
    return ConversationHandler.END

@restricted
def save_question(bot, update):
    lang = select_language(update.effective_user.id)
    question_file = open("questions.txt", "r", encoding="utf-8")
    question = question_file.readline()
    saved_file = open("savedquestions.txt", "a", encoding="utf-8")
    saved_file.write(question)
    question_file.close
    saved_file.close
    bot.send_message(chat_id=update.message.chat_id, text=lang["questionSavedCorrectly"])
    return ANSWER

@restricted
def skip(bot,update):
    lang = select_language(update.effective_user.id)
    bot.send_message(chat_id=update.message.chat_id, text=lang["questionNotAnswered"])
    pop_question(option="enqueue")
    return ConversationHandler.END

@restricted
def cancel(bot, update):
    lang = select_language(update.effective_user.id)  
    bot.send_message(chat_id=update.message.chat_id, text=lang["conversationDeleted"])
    return ConversationHandler.END

@restricted
def reply(bot, update):
    lang = select_language(update.effective_user.id)
    bot.send_message(chat_id=update.message.chat_id, text=lang["answerQuestion"] + " \n")
    question_file = open("questions.txt", "r", encoding="utf-8")
    question = question_file.readline()
    if(question == ""):
        bot.send_message(chat_id=update.message.chat_id, text=lang["noQuestions"])
        return ConversationHandler.END
    bot.send_message(chat_id=update.message.chat_id, text=question)
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
        bot.send_message(chat_id=update.message.chat_id, text=(question[0] + " " + question[2]))
        n = n + 1
    if(n == 0):
        bot.send_message(chat_id=update.message.chat_id, text=lang["questionsAnswered"])
     
@restricted
def sendNewsletter(bot, update):
    lang = select_language(update.effective_user.id)
    keyboard = [[InlineKeyboardButton(lang["newsletterUnsubscribe"], callback_data="unsubscribe")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    idListFile = open("userIDs.json", "r", encoding="utf-8")
    idList = json.load(idListFile)
    with open("newsletter.json", "r", encoding="utf-8") as f:
        data = json.load(f) 
        for x in data:
            if(lang == lang_en): 
                for userId in idList: # send newsletter to all the subscribed users
                    bot.send_message(chat_id=userId['id'], text=x['DescriptionENG'], reply_markup=reply_markup)
            else:
                for userId in idList: 
                    bot.send_message(chat_id=userId['id'], text=x['DescriptionITA'], reply_markup=reply_markup)
        f.close()
    idListFile.close()

@restricted 
def showsaved(bot, update):
    lang = select_language(update.effective_user.id)
    question_file = open("savedquestions.txt", "r", encoding="utf-8")
    questions = question_file.readlines()
    n = 0
    for q in questions:
        question = q.split("-")
        bot.send_message(chat_id=update.message.chat_id, text=(question[0] + " " + question[2]))
        n = n + 1
    if(n == 0):
        bot.send_message(chat_id=update.message.chat_id, text=lang["noQuestionsSaved"])

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
