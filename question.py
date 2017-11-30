class Question:
    def __init__(self, title, question, answers, timestamp, post_id):
        self.title = title
        #self.user_id = user_id
        #self.user_link = user_link
        self.question = question
        self.answers = answers
        self.timestamp = timestamp
        self.post_id = post_id
    def jsonable(self):
        return self.__dict__
