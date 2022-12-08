from datetime import datetime as dt

class Topic:
    def __init__(self, id, title, description, user_id):
        self.id = id
        self.title = title
        self.description = description
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


