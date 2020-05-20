import filters
import time
import telegram
from telegram.ext import Updater
import datetime
import re
import html2text
from urllib.request import urlopen
from functools import wraps
from telegram.ext import MessageHandler
from datetime import timedelta
from datetime import datetime
from threading import Timer
from telegram import ChatAction
# Lang dictionaries
from lang import lang_en
from lang import lang_it

emoji = ["📚", "", "📅", "", "⏰", "", "📩", "📩", ""]
users = {} # Dictionary which stores language used by every user
days = {'Lunedì':'Monday','Martedì':'Tuesday','Mercoledì':'Wednesday','Giovedì':'Thursday','Venerdì':'Friday','Sabato':'Saturday','Domenica':'Sunday'}

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

def has_key_in(dictionary, string):
        for k in dictionary:
                if(k in string):
                        return k
        return ''

def translate(string):
        day = has_key_in(days, string)
        if(day != ''):
                string=string.replace(day, days[day]) 
        return string

send_typing_action = send_action(ChatAction.TYPING)
def tutoringFile():
        fp = urlopen("http://hknpolito.org/tutoring/")
        mybytes = fp.read()
        mystr = mybytes.decode("utf8")
        fp.close()
        mystr = html2text.html2text(mystr)
        m=mystr.split("* ###")
        m.pop(0)
        out_file = open("tutoring.txt", "w", encoding="utf-8")
        for el in m:
                sub_els=el.split('\n', 11) #2 useless + 9 useful
                sub_els.pop()
                sub_els=sub_els[2:] #remove first 2 useless
                sub_els[6] = sub_els[6] + " "

                ### join two tutors element into one element list ###
                sub_els[6:8] = [''.join(map(str,sub_els[6:8]))] 

                ### create list with two elements (two tutors) ###
                tutors = sub_els[6].split('Tutor:')
                newlist = 'Tutor:'.join(tutors[:2]), 'Tutor:'.join(tutors[2:])
                newlist = list(newlist)
                newlist[1] = 'Tutor:' + newlist[1]

                ### insert new list in old sub_els list in the correct position ###
                del sub_els[6]
                for i in range(len(newlist)): 
                        sub_els.insert(i + 6, newlist[i]) 

                ### write on file ###
                j=0 
                numTutor=0
                for sub_el in sub_els:
                        if("Tutor:" in sub_el):
                                numTutor=numTutor+1
                        else:
                                numTutor=0
                        if("Tutor:" in sub_el and len(sub_el) < 7):
                                out_file.write(emoji[j] + " Tutor: -" + "\n" ) #remove '#' leading chars 
                                j=j+1
                                continue
                        if("######" in sub_el):
                                out_file.write("" + "\n" ) #remove '#' leading chars 
                                j=j+1
                                continue
                        if(numTutor<2):
                                out_file.write(emoji[j] + " " + str.lstrip(sub_el, "#### ") + "\n" ) #remove '#' leading chars         
                        else:
                                out_file.write("📩 " + str.lstrip(sub_el, "#### ") + "\n" ) #remove '#' leading chars         
                        j=j+1  

        out_file.close()
        x=datetime.today()
        y=x+timedelta(days=1)
        delta_t = y-x
        secs = delta_t.seconds +1
        t=Timer(secs, tutoringFile)
        t.start()


#-- Study groups handler 
 
from itertools import islice 

@send_typing_action  
def tutoring(bot, update):
        in_file=open("tutoring.txt", "r", encoding="utf-8")
        user_id = str(update.effective_user.id)
        empty=True
        while True:
                next_tutoring_group= list(islice(in_file, 9)) #9 = 5 rows + 4 '\n'
                if(empty):
                        if not next_tutoring_group:
                                lang = select_language(user_id)
                                bot.send_message(chat_id=update.message.chat_id, text=lang["noStudyGroups"])
                                in_file.close()
                                break
                t = ""
                for i in next_tutoring_group:
                        if(users.get(user_id) == None or users.get(user_id) == "EN"): 
                                i = translate(i) #translate in english
                        t = t + i
                empty = False
                bot.send_message(chat_id=update.message.chat_id, text=t)

# Language selection
def select_language(user_id):
    if users.get(user_id) == None or users.get(user_id) == "EN":
        return lang_en
    else:
        return lang_it
