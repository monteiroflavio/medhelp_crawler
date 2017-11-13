class Subtopic:
    def __init__(self, title, link):
        self.title = title
        self.link = link
        self.questions_links = []
    def jsonable(self):
        return self.__dict__
