from mention_bot import MentionAction
from utils import is_process_tweet_needed

import dicta_utils


class NikudAction(MentionAction):
    def __init__(self, api, is_production):
        self.api = api
        self.is_production = is_production

    def run(self, mention):
        comment = self.api.get_status(mention.in_reply_to_status_id)
        if is_process_tweet_needed(mention):
            status = dicta_utils.get_dicta_tweet_text(comment.text, comment.user.screen_name)
            if self.is_production:
                self.api.update_status(status=status, in_reply_to_status_id=mention.id)
