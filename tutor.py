from telegram.ext import CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import datetime
import html2text
from urllib.request import urlopen
from functools import wraps
from datetime import timedelta
from datetime import datetime
from threading import Timer
from telegram import ChatAction
# Lang dictionaries
from lang import lang_en
from lang import lang_it

emoji = ["📚", "", "📅", "", "⏰", "", "📩", "📩", ""]
users = {} # Dictionary which stores language used by every user
days = {'Monday':'Lunedì','Tuesday':'Martedì','Wednesday':'Mercoledì','Thursday':'Giovedì','Friday':'Venerdì','Saturday':'Sabato','Sunday':'Domenica'}


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

def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func


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
def tutoring(update: Update, context: CallbackContext) -> None:
        in_file=open("tutoring.txt", "r", encoding="utf-8")
        user_id = str(update.effective_user.id)
        empty=True
        while True:
                next_tutoring_group= list(islice(in_file, 9)) #9 = 5 rows + 4 '\n'
                if(empty):
                        if not next_tutoring_group:
                                lang = select_language(user_id)
                                #bot.send_message(chat_id=update.message.chat_id, text=lang["noStudyGroups"])
                                in_file.close()
                                break
                t = ""
                for i in next_tutoring_group:
                        if(users.get(user_id) == "IT"): 
                                i = translate(i) #translate in italian
                        t = t + i
                empty = False
                context.bot.send_message(chat_id=update.message.chat_id, text=t)
        #inline_keyboard = [[InlineKeyboardButton("Algoritmi e programmazione", url="https://t.me/hkn_algo")]]
        inline_keyboard = [[InlineKeyboardButton("Algoritmi e programmazione", url="https://t.me/hkn_algo")], [InlineKeyboardButton("Elettrotecnica", url="https://t.me/joinchat/AAAAAFhtPg-zhW_Wgd5tXw")], [InlineKeyboardButton("Sistemi operativi", url="https://t.me/joinchat/BDXJKB2iuB1mBZLTjh9hgQ")], [InlineKeyboardButton("Sistemi elettronici, tecnologie e misure", url="https://t.me/joinchat/BDXJKEfBdulUjK8wyvOLhQ")], [InlineKeyboardButton("Teoria dei segnali e delle comunicazioni", url="https://t.me/joinchat/BDXJKBo-X259OnONBNl8iQ")], [InlineKeyboardButton("Elettronica Applicata (Elettronica)", url="https://t.me/joinchat/AAAAAEX055_0n_PouPzjAg")], [InlineKeyboardButton("Architetture dei sistemi di elaborazione", url="https://t.me/joinchat/AAAAAElCC1jy_ue6AniDnA")], [InlineKeyboardButton("Reti di calcolatori", url="https://t.me/joinchat/BDXJKEl0zW9Zr-ka5GmxiA")], [InlineKeyboardButton("Campi Elettromagnetici (elettronica)", url="https://t.me/joinchat/BDXJKBnDkuQl00-SFa8AiQ")]]
        context.bot.send_message(chat_id=update.message.chat_id, text=lang["tutorText"], reply_markup=InlineKeyboardMarkup(inline_keyboard))

# Language selection
def select_language(user_id):
    if users.get(user_id) == None or users.get(user_id) == "EN":
        return lang_en
    else:
        return lang_it
