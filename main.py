import os
import re
import time
import schedule as schedule
import tweepy

import dicta_utils


def is_hebrew(text):
    return bool(re.match('^[א-ת]*$', text))


def is_percentage_hebrew(text, percent):
    count = 0
    for char in text:
        if is_hebrew(char):
            count += 1
    if len(text) * percent > count:
        return False
    return True


def is_process_tweet_needed(tweet):
    is_mention = '@' in tweet.text
    is_link = 'urls' in tweet.entities and tweet.entities['urls']
    is_length_ok = 20 < len(tweet.text) < 220
    is_user_protected = tweet.user.protected
    return not is_mention and not is_link and not is_user_protected and is_length_ok and \
        is_percentage_hebrew(tweet.text, 0.8)


def get_nikud_timeline(api, user_id, num_tweets):
    result = []
    tweet_count = 0
    for status in tweepy.Cursor(api.home_timeline, id=user_id, exclude_replies=True).items():
        if tweet_count >= num_tweets:
            break
        if is_process_tweet_needed(status):
            tweet_count += 1
            result.append(dicta_utils.get_dicta_nikud(status.text) + '\n\n' + 'מקור: ' + '@' + status.user.screen_name)
    return result


def tweet_nikud(api, num_tweets):
    nikud_timeline = get_nikud_timeline(api, api.me().id, num_tweets)
    for tweet in nikud_timeline:
        print('Tweeting: ' + tweet.replace('\n', '\\n'))
        if os.environ.get('IS_PRODUCTION', 'True') == 'True':
            api.update_status(tweet)


if __name__ == '__main__':
    auth = tweepy.OAuthHandler(os.environ['SHIRBOT_CONSUMER_KEY'], os.environ['SHIRBOT_CONSUMER_VALUE'])
    auth.set_access_token(os.environ['SHIRBOT_ACCESS_TOKEN_KEY'], os.environ['SHIRBOT_ACCESS_TOKEN_VALUE'])

    tweepy_api = tweepy.API(auth, wait_on_rate_limit=True)
    tweet_nikud(tweepy_api, 3)
    schedule.every(3).hours.do(tweet_nikud, tweepy_api, 3)
    schedule.every(15).minutes.do(print, "I'm Alive...")
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as exp:
            print('ERROR! {}'.format(str(exp)))
