import json
import os
import random
import re
import time

import schedule as schedule
import tweepy

import requests


def send_dicta_request(data):
    body = {"task": "nakdan", "data": str(data), "genre": "modern"}
    headers = {'Content-type': 'text/plain;charset=UTF-8', 'accept-encoding': 'gzip, deflate, br'}
    response = requests.post('https://nakdan-3-0a.loadbalancer.dicta.org.il/api', json=body, headers=headers)
    return json.loads(response.text)


def dicta_words_as_list(dicta_api_result):
    result = []
    for word in dicta_api_result:
        if len(word['options']) > 0:
            result.append(word['options'][0].replace('|', ''))
        else:
            result.append(word['word'])
    return result


def replace_random_spaces_with_newline(dicta_list):
    num_chars_between_spaces = 15
    num_chars_in_list = len(''.join(dicta_list))
    num_spaces = 0 if num_chars_in_list <= num_chars_between_spaces else int(num_chars_in_list / num_chars_between_spaces)
    space_indexes = [i for i, x in enumerate(dicta_list) if x == ' ']
    spaces_to_replace = random.choices(space_indexes, k=num_spaces)
    for i in spaces_to_replace:
        dicta_list[i] = '\n'
    return dicta_list


def get_dicta_nikud_as_list(text):
    return dicta_words_as_list(send_dicta_request(text))


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


def get_dicta_nikud(text):
    return ''.join(replace_random_spaces_with_newline(get_dicta_nikud_as_list(text)))


def get_nikud_timeline(api, user_id, num_tweets):
    result = []
    timeline = api.home_timeline(id=user_id)
    tweet_count = 0
    for status in timeline:
        if tweet_count >= num_tweets:
            break
        if '@' not in status.text and \
                'https://' not in status.text and \
                10 < len(status.text) < 100 and is_percentage_hebrew(status.text, 0.8) and not status.user.protected:
            tweet_count += 1
            result.append(get_dicta_nikud(status.text) + '\n\n' + 'מקור: ' + '@' + status.user.screen_name)
    return result


def tweet_nikud(api, api_for_timeline, user_id, num_tweets):
    nikud_timeline = get_nikud_timeline(api_for_timeline, user_id, num_tweets)
    for tweet in nikud_timeline:
        print('Tweeting: ' + tweet.replace('\n', ' '))
        api.update_status(tweet)


if __name__ == '__main__':
    auth = tweepy.OAuthHandler(os.environ['SHIRBOT_CONSUMER_KEY'], os.environ['SHIRBOT_CONSUMER_VALUE'])
    auth.set_access_token(os.environ['SHIRBOT_ACCESS_TOKEN_KEY'], os.environ['SHIRBOT_ACCESS_TOKEN_VALUE'])

    auth_for_timeline = tweepy.OAuthHandler(os.environ['TWITTER_CONSUMER_KEY'], os.environ['TWITTER_CONSUMER_VALUE'])
    auth_for_timeline.set_access_token(os.environ['TWITTER_ACCESS_TOKEN_KEY'], os.environ['TWITTER_ACCESS_TOKEN_VALUE'])

    tweepy_api_for_timeline = tweepy.API(auth_for_timeline, wait_on_rate_limit=True)
    tweepy_api = tweepy.API(auth, wait_on_rate_limit=True)

    user_id = tweepy_api_for_timeline.me().id

    schedule.every(3).hours.do(tweet_nikud, tweepy_api, tweepy_api_for_timeline, user_id, 3)
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as exp:
            print('ERROR! {}'.format(str(exp)))
