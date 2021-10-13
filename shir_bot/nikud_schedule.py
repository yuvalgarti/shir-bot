import logging
import os
import time

import schedule
import tweepy

from shir_bot import utils, dicta_utils
from shir_bot.utils import is_process_tweet_needed

logger = logging.getLogger(__name__)


def get_nikud_timeline(api, user_id, num_tweets):
    result = []
    tweet_count = 0
    for status in tweepy.Cursor(api.home_timeline, id=user_id, exclude_replies=True).items():
        if tweet_count >= num_tweets:
            break
        if is_process_tweet_needed(api, status):
            tweet_text = utils.get_tweet_full_text(api, status)
            nikud_tweet = dicta_utils.get_dicta_nikud(tweet_text)
            if len(nikud_tweet) < 280:
                tweet_count += 1
                result.append({'nikud': nikud_tweet,
                               'screen_name': status.user.screen_name,
                               'tweet_id': status.id})
    return result


def tweet_nikud(api, num_tweets):
    logger.info('nikud_schedule task started')
    nikud_timeline = get_nikud_timeline(api, api.me().id, num_tweets)
    for tweet_with_metadata in nikud_timeline:
        logger.info('Tweeting: ' + tweet_with_metadata['nikud'].replace('\n', '\\n'))
        if os.environ.get('IS_PRODUCTION', 'True') == 'True':
            status = api.update_status(tweet_with_metadata['nikud'])
            api.update_status(status=('@' + api.me().screen_name + ' ' + 'מקור'), in_reply_to_status_id=status.id,
                              attachment_url='https://twitter.com/{}/status/{}'.format(tweet_with_metadata['screen_name'],
                                                                                       tweet_with_metadata['tweet_id']))
    logger.info('nikud_schedule task ended')


def nikud_scheduled(api):
    # tweet_nikud(api, 3)
    logger.info('nikud_schedule started')
    job = schedule.every(4).hours.do(tweet_nikud, api, 3)

    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as exp:
            logger.exception('ERROR! {}'.format(str(exp)))
            schedule.cancel_job(job)
            job = schedule.every(4).hours.do(tweet_nikud, api, 3)
