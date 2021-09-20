import os
import re
import time

import schedule as schedule
import tweepy

import dicta_utils

LAST_TWEET_ID = 1

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
    is_link = 'https://' in tweet.text
    is_length_ok = 10 < len(tweet.text) < 100
    is_user_protected = tweet.user.protected
    return not is_mention and not is_link and not is_user_protected and is_length_ok and \
        is_percentage_hebrew(tweet.text, 0.8)


def get_nikud_timeline(api, user_id, num_tweets):
    global LAST_TWEET_ID
    result = []
    print(LAST_TWEET_ID)
    timeline = api.home_timeline(id=user_id, since_id=LAST_TWEET_ID, exclude_replies=True)
    tweet_count = 0
    for status in timeline:
        if tweet_count >= num_tweets:
            break
        if is_process_tweet_needed(status):
            tweet_count += 1
            result.append(dicta_utils.get_dicta_nikud(status.text) + '\n\n' + 'מקור: ' + '@' + status.user.screen_name)
            if status.id > LAST_TWEET_ID:
                LAST_TWEET_ID = status
    return result


def tweet_nikud(api, api_for_timeline, num_tweets):
    nikud_timeline = get_nikud_timeline(api_for_timeline, api_for_timeline.me().id, num_tweets)
    for tweet in nikud_timeline:
        print('Tweeting: ' + tweet.replace('\n', ' '))
        if os.environ.get('IS_PRODUCTION', 'True') == 'True':
            api.update_status(tweet)


if __name__ == '__main__':
    auth = tweepy.OAuthHandler(os.environ['SHIRBOT_CONSUMER_KEY'], os.environ['SHIRBOT_CONSUMER_VALUE'])
    auth.set_access_token(os.environ['SHIRBOT_ACCESS_TOKEN_KEY'], os.environ['SHIRBOT_ACCESS_TOKEN_VALUE'])

    auth_for_timeline = tweepy.OAuthHandler(os.environ['TWITTER_CONSUMER_KEY'], os.environ['TWITTER_CONSUMER_VALUE'])
    auth_for_timeline.set_access_token(os.environ['TWITTER_ACCESS_TOKEN_KEY'], os.environ['TWITTER_ACCESS_TOKEN_VALUE'])

    tweepy_api_for_timeline = tweepy.API(auth_for_timeline, wait_on_rate_limit=True)
    tweepy_api = tweepy.API(auth, wait_on_rate_limit=True)

    schedule.every(3).hours.do(tweet_nikud, tweepy_api, tweepy_api_for_timeline, 3)
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as exp:
            print('ERROR! {}'.format(str(exp)))
