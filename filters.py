# Custom filters for message handling

from telegram.ext import MessageFilter
from lang import lang_en, lang_it


class FilterTutoring(MessageFilter):
    def filter(self, message):
        return lang_en["studygroups"].lower() == message.text.lower() or lang_it[
            "studygroups"].lower() == message.text.lower()


class FilterAbout(MessageFilter):
    def filter(self, message):
        return lang_en["about"].lower() == message.text.lower() or lang_it["about"].lower() == message.text.lower()


class FilterNews(MessageFilter):
    def filter(self, message):
        return lang_en["news"].lower() == message.text.lower() or lang_it["news"].lower() == message.text.lower()


class FilterEvents(MessageFilter):
    def filter(self, message):
        return lang_en["events"].lower() == message.text.lower() or lang_it["events"].lower() == message.text.lower()


class FilterNewsletter(MessageFilter):
    def filter(self, message):
        return lang_en["newsletter"].lower() == message.text.lower() or lang_it[
            "newsletter"].lower() == message.text.lower()


class FilterQuestions(MessageFilter):
    def filter(self, message):
        return lang_en["askus"].lower() == message.text.lower() or lang_it["askus"].lower() == message.text.lower()


class FilterDrive(MessageFilter):
    def filter(self, message):
        return lang_en["drive"].lower() == message.text.lower() or lang_it["drive"].lower() == message.text.lower()


class FilterBack(MessageFilter):
    def filter(self, message):
        return lang_en["back"].lower() == message.text.lower() or lang_it["back"].lower() == message.text.lower()


class FilterContact(MessageFilter):
    def filter(self, message):
        return lang_en["contact"].lower() == message.text.lower() or lang_it["contact"].lower() == message.text.lower()


class FilterMembers(MessageFilter):
    def filter(self, message):
        return lang_en["members"].lower() == message.text.lower() or lang_it["members"].lower() == message.text.lower()


class Filterelectronicengineeringgroups(MessageFilter):
    def filter(self, message):
        return lang_en["electronicengineeringgroups"].lower() == message.text.lower() or lang_it[
            "electronicengineeringgroups"].lower() == message.text.lower()


class FilterIt(MessageFilter):
    def filter(self, message):
        return lang_en["lang_ita"].lower() == message.text.lower() or lang_it[
            "lang_ita"].lower() == message.text.lower()


class FilterEn(MessageFilter):
    def filter(self, message):
        return lang_en["lang_eng"].lower() == message.text.lower() or lang_it[
            "lang_eng"].lower() == message.text.lower()
