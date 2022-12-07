from datetime import datetime as dt

class Topic:
    def __init__(self, id, title, content, user_id):
        self.id = id
        self.title = title
        self.content = content
        self.comments = []
        self.user_id = user_id
        self.created_at = dt.now()
        self.updated_at = dt.now()

    @staticmethod
    def insert():
        pass

    @staticmethod
    def find():
        pass

    @staticmethod
    def find_one():
        pass

    @staticmethod
    def update():
        pass

    @staticmethod
    def delete():
        pass


