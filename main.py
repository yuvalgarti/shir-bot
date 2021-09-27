import logging
import os
import sys
import threading
import tweepy
from mention_bot import MentionHandler

from shir_bot.firebase_service import FirebaseService
from shir_bot.nikud_action import NikudAction
from shir_bot.nikud_schedule import nikud_scheduled

if __name__ == '__main__':
    auth = tweepy.OAuthHandler(os.environ['SHIRBOT_CONSUMER_KEY'], os.environ['SHIRBOT_CONSUMER_VALUE'])
    auth.set_access_token(os.environ['SHIRBOT_ACCESS_TOKEN_KEY'], os.environ['SHIRBOT_ACCESS_TOKEN_VALUE'])

    firebase_config = {
        'apiKey': os.environ['SHIRBOT_FIREBASE_API_KEY'],
        'authDomain': os.environ['SHIRBOT_FIREBASE_AUTH_DOMAIN'],
        'databaseURL': os.environ['SHIRBOT_FIREBASE_DB_URL'],
        'storageBucket': os.environ['SHIRBOT_FIREBASE_STORAGE_BUCKET']
    }

    is_production = os.environ.get('IS_PRODUCTION', 'True') == 'True'

    tweepy_api = tweepy.API(auth, wait_on_rate_limit=True)
    firebase_db = FirebaseService(firebase_config)

    log_modules = ['shir_bot', 'mention_bot']
    logFormat = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logFormat)

    for module_name in log_modules:
        logger = logging.getLogger(module_name)
        logger.setLevel('DEBUG')
        logger.addHandler(console_handler)

    nikud_mention_action = NikudAction(tweepy_api, is_production)
    mention_handler = MentionHandler(tweepy_api,
                                     nikud_mention_action,
                                     firebase_db,
                                     is_production,
                                     int(os.environ.get('SCREENSHOT_TIMEOUT', 30)),
                                     int(os.environ.get('RETRY_COUNT', 3)))

    scheduled_task = threading.Thread(name='scheduled_task', target=nikud_scheduled, args=(tweepy_api,))
    mention_task = threading.Thread(name='mention_task', target=mention_handler.run)

    scheduled_task.start()
    mention_task.start()
