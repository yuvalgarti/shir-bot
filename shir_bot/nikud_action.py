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
                status = dicta_utils.get_dicta_nikud(tweet_text)
            else:
                status = 'הציוץ לא עומד במגבלות: הציוץ צריך להיות בין 20 ל 220 תווים, אסור שיהיו קישורים בציוץ, ' \
                         'הציוץ צריך להיות לפחות 80% עברית '

        status_part_2 = None
        if 280 < len(status) < 560:
            status_part_1 = status[:int(len(status)/2)]
            status_part_2 = status[int(len(status)/2):]
            status = status_part_1
        if len(status) >= 560:
            status = 'הַצִּיּוּץ (כּוֹלֵל הַנִּקּוּד) אָרֹךְ מִדַּי...'

        status = '@' + mention.user.screen_name + ' ' + status
        self.logger.info('From mention: ' + status.replace('\n', '\\n'))
        if status_part_2:
            status_part_2 = '@' + mention.user.screen_name + ' @' + self.api.me().screen_name + ' ' + status_part_2
            self.logger.info('From mention part 2: ' + status_part_2.replace('\n', '\\n'))
        if self.is_production:
            created_tweet = self.api.update_status(status=status, in_reply_to_status_id=mention.id)
            if status_part_2:
                self.api.update_status(status=status_part_2, in_reply_to_status_id=created_tweet.id)
