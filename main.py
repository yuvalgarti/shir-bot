import os
import re
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
    timeline = api.home_timeline(id=user_id, exclude_replies=True)
    tweet_count = 0
    for status in timeline:
        if tweet_count >= num_tweets:
            break
        if is_process_tweet_needed(status):
            tweet_count += 1
            result.append(dicta_utils.get_dicta_nikud(status.text) + '\n\n' + 'מקור: ' + '@' + status.user.screen_name)
    return result


def tweet_nikud(api, api_for_timeline, num_tweets):
    nikud_timeline = get_nikud_timeline(api_for_timeline, api_for_timeline.me().id, num_tweets)
    for tweet in nikud_timeline:
        print('Tweeting: ' + tweet.replace('\n', '\\n'))
        if os.environ.get('IS_PRODUCTION', 'True') == 'True':
            api.update_status(tweet)


def nikud_scheduled():
    schedule.every(4).hours.do(tweet_nikud, tweepy_api, tweepy_api_for_timeline, 3)
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

    auth_for_timeline = tweepy.OAuthHandler(os.environ['TWITTER_CONSUMER_KEY'], os.environ['TWITTER_CONSUMER_VALUE'])
    auth_for_timeline.set_access_token(os.environ['TWITTER_ACCESS_TOKEN_KEY'], os.environ['TWITTER_ACCESS_TOKEN_VALUE'])

    firebase_config = {
        'apiKey': os.environ['FIREBASE_API_KEY'],
        'authDomain': os.environ['FIREBASE_AUTH_DOMAIN'],
        'databaseURL': os.environ['FIREBASE_DB_URL'],
        'storageBucket': os.environ['FIREBASE_STORAGE_BUCKET']
    }

    tweepy_api_for_timeline = tweepy.API(auth_for_timeline, wait_on_rate_limit=True)
    tweepy_api = tweepy.API(auth, wait_on_rate_limit=True)
    is_production = os.environ.get('IS_PRODUCTION', 'True') == 'True'

    nikud_mention_action = NikudAction(tweepy_api)
    mention_handler = MentionHandler(tweepy_api,
                                     nikud_mention_action,
                                     FirebaseService(firebase_config),
                                     is_production,
                                     int(os.environ.get('SCREENSHOT_TIMEOUT', 30)),
                                     int(os.environ.get('RETRY_COUNT', 3)))

    b = threading.Thread(name='background', target=nikud_scheduled)
    f = threading.Thread(name='foreground', target=mention_handler.run)

    b.start()
    f.start()
