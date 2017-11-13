class Answer:
    def __init__(self, user_id, user_link, answer, timestamp, votes, post_id):
        self.user_id = user_id
        self.user_link = user_link
        self.answer = answer
        self.timestamp = timestamp
        self.votes = votes
        self.post_id = post_id
    def jsonable(self):
        return self.__dict__
