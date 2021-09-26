from mention_bot import MentionAction

import dicta_utils
import utils
from utils import is_process_tweet_needed


class NikudAction(MentionAction):
    def __init__(self, api, is_production):
        self.api = api
        self.is_production = is_production

    def run(self, mention):
        comment = self.api.get_status(mention.in_reply_to_status_id)
        if is_process_tweet_needed(self.api, comment):
            tweet_text = utils.get_tweet_full_text(self.api, comment)
            status = dicta_utils.get_dicta_tweet_text(tweet_text, comment.user.screen_name)
        else:
            status = 'שימו לב למגבלות שמפורטות כאן: https://twitter.com/shir_bot/status/1442192544058707975'
        status = '@' + mention.user.screen_name + ' ' + status
        print('From mention: ' + status.replace('\n', '\\n'))
        if self.is_production:
            self.api.update_status(status=status, in_reply_to_status_id=mention.id)
