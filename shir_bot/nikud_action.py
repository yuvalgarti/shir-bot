import logging

from mention_bot import MentionAction

from shir_bot import dicta_utils, utils
from shir_bot.utils import is_process_tweet_needed


class NikudAction(MentionAction):
    def __init__(self, api, is_production):
        self.api = api
        self.is_production = is_production
        self.logger = logging.getLogger(__name__)

    def run(self, mention):
        comment = self.api.get_status(mention.in_reply_to_status_id)
        if comment.user.id == self.api.me().id:
            status = 'הַצִּיּוּצִים שֶׁלִּי כְּבָר מְנֻקָּדִים...'
        else:
            if is_process_tweet_needed(self.api, comment):
                tweet_text = utils.get_tweet_full_text(self.api, comment)
                status = dicta_utils.get_dicta_tweet_text(tweet_text, comment.user.screen_name)
            else:
                status = 'הציוץ לא עומד במגבלות: הציוץ צריך להיות בין 20 ל 220 תווים, אסור שיהיו קישורים בציוץ, ' \
                         'הציוץ צריך להיות לפחות 80% עברית '
        status = '@' + mention.user.screen_name + ' ' + status
        if len(status) > 280:
            status = '@' + mention.user.screen_name + ' ' + 'הַצִּיּוּץ (כּוֹלֵל הַנִּקּוּד) אָרֹךְ מִדַּי...'
        self.logger.info('From mention: ' + status.replace('\n', '\\n'))
        if self.is_production:
            self.api.update_status(status=status, in_reply_to_status_id=mention.id)
