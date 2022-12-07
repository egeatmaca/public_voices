class User:
    def __init__(self, id, username, password, created_at, updated_at):
        self.id = id
        self.username = username
        self.password = password
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
