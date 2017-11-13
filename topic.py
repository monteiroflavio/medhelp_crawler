class Topic:
   def __init__(self, title, subtopics):
      self.title = title
      self.subtopics = subtopics
   def jsonable(self):
      return self.__dict__
