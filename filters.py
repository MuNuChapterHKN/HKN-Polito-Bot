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

class FilterNewsletter(BaseFilter):
   def filter(self, message):      
      return lang_en["newsletter"].lower() == message.text.lower() or lang_it["newsletter"].lower() == message.text.lower()

class FilterQuestions(BaseFilter):
   def filter(self, message):      
      return lang_en["askus"].lower() == message.text.lower() or lang_it["askus"].lower() == message.text.lower()

class FilterDrive(BaseFilter):
	def filter(slef, message):
	  return lang_en["drive"].lower() == message.text.lower() or lang_it["drive"].lower() == message.text.lower()

class FilterContact(BaseFilter):
        def filter(self, message):
         return lang_en["contact"].lower() == message.text.lower() or lang_it["contact"].lower() == message.text.lower()
