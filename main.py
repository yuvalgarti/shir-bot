import os
import threading
import time
import schedule as schedule
import tweepy
from mention_bot import MentionHandler
from utils import is_process_tweet_needed

import dicta_utils
from firebase_service import FirebaseService
from nikud_action import NikudAction


def get_nikud_timeline(api, user_id, num_tweets):
    result = []
    tweet_count = 0
    for status in tweepy.Cursor(api.home_timeline, id=user_id, exclude_replies=True).items():
        if tweet_count >= num_tweets:
            break
        if is_process_tweet_needed(status):
            tweet_count += 1
            result.append(dicta_utils.get_dicta_tweet_text(status.text, status.user.screen_name))
    return result


def tweet_nikud(api, num_tweets):
    nikud_timeline = get_nikud_timeline(api, api.me().id, num_tweets)
    for tweet in nikud_timeline:
        print('Tweeting: ' + tweet.replace('\n', '\\n'))
        if os.environ.get('IS_PRODUCTION', 'True') == 'True':
            api.update_status(tweet)


def nikud_scheduled(api):
    tweet_nikud(tweepy_api, 3)
    schedule.every(3).hours.do(tweet_nikud, tweepy_api, 3)
    schedule.every(15).minutes.do(print, "I'm Alive...")

    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as exp:
            print('ERROR! {}'.format(str(exp)))


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
