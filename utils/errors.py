import telegram
from utils.env import ERROR_CHANNEL_ID

def publish_error(bot, e):
    bot.send_message(chat_id=ERROR_CHANNEL_ID, text=e)
    