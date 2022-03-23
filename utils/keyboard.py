# Keyboard.py
# this file handles all the keyboards type
from enum import Enum

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from utils.common import members_list, links


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
    elif type == KeyboardType.NEWSLETTER_UNSUB:     # TODO: This keyboard is never used
        keyboard_unsub = [[InlineKeyboardButton(lang["newsletterUnsubscribe"], callback_data="unsubscribe")]]
        return InlineKeyboardMarkup(keyboard_unsub)
    elif type == KeyboardType.LANGUAGE:
        start_keyboard = [[lang["lang_ita"], lang["lang_eng"]]]
        return telegram.ReplyKeyboardMarkup(start_keyboard, resize_keyboard=True)
    elif type == KeyboardType.ABOUT:
        inline_keyboard = [[InlineKeyboardButton(lang["website"], url=links['website'])],
                           [InlineKeyboardButton(lang["facebook"], url=links['facebook'])],
                           [InlineKeyboardButton(lang["instagram"], url=links['instagram'])],
                           [InlineKeyboardButton(lang["youtube"], url=links['youtube'])]]
        return InlineKeyboardMarkup(inline_keyboard)
    elif type == KeyboardType.DRIVE:
        inline_keyboard = [[InlineKeyboardButton(lang["driveButton"], url=links['public_drive'])]]
        return InlineKeyboardMarkup(inline_keyboard)
    elif type == KeyboardType.ELECTRONICENGINEERINGGROUPS:
        inline_keyboard = [[InlineKeyboardButton(lang["Triennale"], callback_data="Triennale")],
                           [InlineKeyboardButton(lang["Magistrale"], callback_data="Magistrale")]]
        return InlineKeyboardMarkup(inline_keyboard)
    elif type == KeyboardType.MEMBERS:
        # if the user is one of the members show the special buttons
        if user_id in members_list:
            inline_keyboard = [[InlineKeyboardButton(lang["FI"], url=links['formazione_interna'])],
                               [InlineKeyboardButton(lang["TelegramGroups"], callback_data="TelegramGroups")],
                               [InlineKeyboardButton(lang["HRGame"], callback_data="HRGame")],
                               [InlineKeyboardButton(lang["usefulLinks"], callback_data="usefulLinks")]]
            return InlineKeyboardMarkup(inline_keyboard)
    elif type == KeyboardType.GROUPS:
        inline_keyboard = [[InlineKeyboardButton("EtaKazzateNu", url=links['etakazzatenu'])],
                           [InlineKeyboardButton("Eta Kappa InvestmeNu", url=links['eta_kappa_investmenu'])],
                           [InlineKeyboardButton("Eta Krypto Nu", url=links['eta_krypto_nu'])],
                           [InlineKeyboardButton("Eta Kappa PhD", url=links['eta_kappa_phd'])],
                           [InlineKeyboardButton("Eta PN junction NU", url=links['eta_pn_junction_nu'])],
                           [InlineKeyboardButton("HKGirls", url=links['hkgirls'])],
                           [InlineKeyboardButton("BiblioteKappaNu", url=links['bibliotekappanu'])],
                           [InlineKeyboardButton("EtaKappaNerds", url=links['etakappanerds'])],
                           [InlineKeyboardButton("HKRocket League", url=links['hkrocket_leauge'])],
                           [InlineKeyboardButton("EtaKappaMovies", url=links['etakappamovies'])],
                           [InlineKeyboardButton("EtaKappaSports", url=links['etakappasports'])],
                           [InlineKeyboardButton("EtaKoseaMuzzo", url=links['etakoseamuzzo'])],
                           [InlineKeyboardButton("EtanoloKappaNu", url=links['etanolokappanu'])],
                           [InlineKeyboardButton("Hell's Kitchen Nu", url=links['hellskitchennu'])],
                           [InlineKeyboardButton("Eta Kidding Nu", url=links['eta_kidding_nu'])]]
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
