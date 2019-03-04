###Custom filters for message handling###

from telegram.ext import BaseFilter
from lang import lang_en
from lang import lang_it

class FilterTutoring(BaseFilter):
   def filter(self, message):
      return lang_en["studygroups"].lower() == message.text.lower() or lang_it["studygroups"].lower() == message.text.lower()

class FilterAbout(BaseFilter):
   def filter(self, message):
      return lang_en["about"].lower() == message.text.lower() or lang_it["about"].lower() == message.text.lower()

class FilterNews(BaseFilter):
   def filter(self, message):
      return lang_en["news"].lower() == message.text.lower() or lang_it["news"].lower() == message.text.lower()

class FilterEvents(BaseFilter):
   def filter(self, message):      
      return lang_en["events"].lower() == message.text.lower() or lang_it["events"].lower() == message.text.lower()

class FilterQuestions(BaseFilter):
   def filter(self, message):      
      return lang_en["askus"].lower() == message.text.lower() or lang_it["askus"].lower() == message.text.lower()