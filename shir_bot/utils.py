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


def get_tweet_full_text(api, tweet):
    extended_tweet = api.get_status(tweet.id, tweet_mode='extended')
    start_text = int(extended_tweet.display_text_range[0])
    end_text = int(extended_tweet.display_text_range[1])
    return extended_tweet.full_text[start_text:end_text]


def is_process_tweet_needed(api, tweet):
    tweet_text = get_tweet_full_text(api, tweet)

    is_retweet_without_text = 'RT' in tweet_text
    is_link = 'http://' in tweet_text or 'https://' in tweet_text
    is_length_ok = 20 < len(tweet_text) < 220
    is_user_protected = tweet.user.protected
    return not is_retweet_without_text and not is_link and not is_user_protected and is_length_ok and \
           is_percentage_hebrew(tweet_text, 0.8)
