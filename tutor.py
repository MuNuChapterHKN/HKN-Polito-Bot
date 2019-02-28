
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

send_typing_action = send_action(ChatAction.TYPING)

def tutoringFile():
        fp = urlopen("http://hknpolito.org/tutoring/")
        mybytes = fp.read()
        mystr = mybytes.decode("utf8")
        fp.close()
        mystr = html2text.html2text(mystr)
        m=mystr.split("* ###")
        m.pop(0)
        out_file= open("tutoring.txt", "w", encoding="utf-8")
        for el in m:
                sub_els=el.split('\n',7)
                sub_els.pop()
                sub_els=sub_els[2:]
                for sub_el in sub_els:
                        out_file.write(str.lstrip(sub_el, "#### ") + "\n" )
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
        while True:
                next_tutoring_group= list(islice(in_file, 5))
                if not next_tutoring_group :
                        in_file.close()
                        break
                t = ""
                for i in next_tutoring_group:
                        t= t + i
                bot.send_message(chat_id=update.message.chat_id, text=t)

        