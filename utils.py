import re


def is_hebrew(text):
    return bool(re.match('^[א-ת]*$', text))


def is_percentage_hebrew(text, percent):
    count = 0
    for char in text:
        if is_hebrew(char) or char == ' ' or char == '\n':
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

