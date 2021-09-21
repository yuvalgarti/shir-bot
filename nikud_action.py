from mention_bot import MentionAction
from utils import is_process_tweet_needed

import dicta_utils


class NikudAction(MentionAction):
    def __init__(self, api):
        self.api = api

    def run(self, mention):
        comment = self.api.get_status(mention.in_reply_to_status_id)
        if is_process_tweet_needed(mention):
            status = dicta_utils.get_dicta_nikud(comment.text) + '\n\n' + 'מקור: ' + '@' + comment.user.screen_name
            self.api.update_status(status=status, in_reply_to_status_id=mention.id)
