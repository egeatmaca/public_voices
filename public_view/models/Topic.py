class Topic:
    def __init__(self, id, title, content, user_id, created_at, updated_at):
        self.id = id
        self.title = title
        self.content = content
        self.comments = []
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at

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


