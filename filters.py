###Custom filters for message handling###

from telegram.ext import BaseFilter

class FilterTutoring(BaseFilter):
   def filter(self, message):
      return 'study groups' == message.text.lower() or 'tutoring' == message.text.lower()

class FilterAbout(BaseFilter):
   def filter(self, message):
      return 'about hkn' == message.text.lower()

class FilterNews(BaseFilter):
   def filter(self, message):
      return 'news' == message.text.lower()

class FilterEvents(BaseFilter):
   def filter(self, message):      
      return 'events' == message.text.lower()

class FilterQuestions(BaseFilter):
   def filter(self, message):      
      return 'ask us something' == message.text.lower()

class FilterAnswers(BaseFilter):
   def filter(self, message):       
      return "?" in message.text.lower() 