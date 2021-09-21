import pyrebase

import mention_bot


class FirebaseService(mention_bot.LastMentionService):
    def __init__(self, firebase_config):
        self.db = pyrebase.initialize_app(firebase_config).database()

    def get_last_mention(self):
        return self.db.child('shirbot_last_mention_id').get().val()

    def set_last_mention(self, last_mention):
        self.db.child('shirbot_last_mention_id').set(str(last_mention))
