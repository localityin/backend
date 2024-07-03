class ConversationEngine():
    def __init__(self, db, user_id) -> None:
        self.conversation = db
        self.loading = True
        self.user_id = user_id
        pass

    def sentiment_analysis(self):
        # pass part of or whole conversation here ig? will come back to this later
        # also this needs to be ridiculously fast
        pass

    def reply(self):
        user_sentiment = self.sentiment_analysis()
        message = "Message received processing."
        self.loading = False
        return message
