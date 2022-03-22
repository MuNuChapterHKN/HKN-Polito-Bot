import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ['DATABASE_URL']
CYPHERKEY = os.environ['HKN_BOT_CIPHERKEY']
BOT_TOKEN = os.environ['HKN_BOT_TOKEN']
WEB_PASSWORD = os.environ['HKN_WEB_PASSWORD']
ERROR_CHANNEL_ID = os.environ['HKN_ERROR_CHANNEL_ID']