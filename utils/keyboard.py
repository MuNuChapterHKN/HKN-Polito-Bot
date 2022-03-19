# Keyboard.py
# this file handles all the keyboards type
from enum import Enum

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from utils.common import members_list


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
    UNDO = 11


def get_keyboard(type: KeyboardType, lang, user_id):
    if type == KeyboardType.BACK:
        inline_keyboard = [[InlineKeyboardButton(lang["back"], callback_data="back")]]
        return InlineKeyboardMarkup(inline_keyboard)
    elif type == KeyboardType.UNDO:
        custom_keyboard = [[lang["back"]]]
        return telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    elif type == KeyboardType.NEWSLETTER_CONFIRM:
        keyboard_confirm = [[InlineKeyboardButton(lang["newsletterConfirm"], callback_data="confirm")],
                            [InlineKeyboardButton(lang["back"], callback_data="back")]]
        return InlineKeyboardMarkup(keyboard_confirm)
    elif type == KeyboardType.NEWSLETTER_UNSUB:
        keyboard_unsub = [[InlineKeyboardButton(lang["newsletterUnsubscribe"], callback_data="unsubscribe")]]
        return InlineKeyboardMarkup(keyboard_unsub)
    elif type == KeyboardType.LANGUAGE:
        start_keyboard = [[lang["lang_ita"], lang["lang_eng"]]]
        return telegram.ReplyKeyboardMarkup(start_keyboard, resize_keyboard=True)
    elif type == KeyboardType.ABOUT:
        inline_keyboard = [[InlineKeyboardButton(lang["website"], url="< LINK >")],
                           [InlineKeyboardButton(lang["facebook"], url="< LINK >")],
                           [InlineKeyboardButton(lang["instagram"], url="< LINK >")],
                           [InlineKeyboardButton(lang["youtube"], url="< LINK >")]]
        return InlineKeyboardMarkup(inline_keyboard)
    elif type == KeyboardType.DRIVE:
        inline_keyboard = [[InlineKeyboardButton(lang["driveButton"], url="< LINK >")]]
        return InlineKeyboardMarkup(inline_keyboard)
    elif type == KeyboardType.ELECTRONICENGINEERINGGROUPS:
        inline_keyboard = [[InlineKeyboardButton(lang["Triennale"], callback_data="Triennale")],
                           [InlineKeyboardButton(lang["Magistrale"], callback_data="Magistrale")]]
        return InlineKeyboardMarkup(inline_keyboard)
    elif type == KeyboardType.MEMBERS:
        # if the user is one of the members show the special buttons
        if user_id in members_list:
            inline_keyboard = [[InlineKeyboardButton(lang["FI"], url="< LINK >")],
                               [InlineKeyboardButton(lang["TelegramGroups"], callback_data="TelegramGroups")],
                               [InlineKeyboardButton(lang["HRGame"], callback_data="HRGame")],
                               [InlineKeyboardButton(lang["usefulLinks"], callback_data="usefulLinks")]]
            return InlineKeyboardMarkup(inline_keyboard)
    elif type == KeyboardType.GROUPS:
        inline_keyboard = [[InlineKeyboardButton("EtaKazzateNu", url="< ETAKAZZATENU LINK >")],
                           [InlineKeyboardButton("HKN Drive", url="< DRIVE LINK >")],
                           [InlineKeyboardButton("HKN-Polito Discord Server", url="< DISCORD SERVER LINK >")],
                           [InlineKeyboardButton("Eta Kappa InvestmeNu", url="< ETA KAPPA INVESTMENU LINK >")],
                           [InlineKeyboardButton("Eta Krypto Nu", url="< ETA KRYPTO NU LINK >")],
                           [InlineKeyboardButton("HKGirls", url="< HKGIRLS LINK >")],
                           [InlineKeyboardButton("Eta PN junction NU", url="< ETA PN JUNCTION NU LINK >")],
                           [InlineKeyboardButton("Eta Kappa PhD", url="< ETA KAPPA PHD LINK >")],
                           [InlineKeyboardButton("hknMUsicNUChapter", url="< HKN MUSIC LINK >")],
                           [InlineKeyboardButton("BiblioteKappaNu", url="< BIBLIOTAKAPPANU LINK >")],
                           [InlineKeyboardButton("EtaKappaNerds", url="< ETAKAPPANERDS LINK >")],
                           [InlineKeyboardButton("HKRocket League", url="< HKROCKET LEAGUE LINK >")],
                           [InlineKeyboardButton("EtaKappaMovies", url="< ETAKAPPAMOVIES LINK >")],
                           [InlineKeyboardButton("EtaKappaSports", url="< ETAKAPPASPORTS LINK >")],
                           [InlineKeyboardButton("EtaKoseaMuzzo", url="< ETAKOSEAMUZZO LINK >")],
                           [InlineKeyboardButton("EtanoloKappaNu", url="< ETANOLOKAPPANU LINK >")],
                           [InlineKeyboardButton("Eta Kidding Nu", url="< ETAMEMENU LINK >")],
                           [InlineKeyboardButton("HKN x gif", url="< HKN x GIF LINK >")]]
        return InlineKeyboardMarkup(inline_keyboard)
    else:
        # if the user is one of the members show the members keyboard
        if user_id in members_list:
            custom_keyboard = [[lang["events"], lang["news"]], [lang["studygroups"], lang["askus"]],
                               [lang["newsletter"], lang["drive"]], [lang["about"], lang["contact"]],
                               [lang["members"], lang["electronicengineeringgroups"]]]
        else:
            custom_keyboard = [[lang["events"], lang["news"]], [lang["studygroups"], lang["askus"]],
                               [lang["newsletter"], lang["drive"]], [lang["about"], lang["contact"]],
                               [lang["electronicengineeringgroups"]]]
        return telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
