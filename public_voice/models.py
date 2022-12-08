from pymongo import MongoClient
import os
from datetime import datetime as dt

class Model:
    client = MongoClient(os.environ.get('MONGO_URI'))

    def __init__(self, collection):
        self.collection = collection
    
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

class Topic(Model):
    def __init__(self, id, title, description, user_id):
        self.id = id
        self.title = title
        self.description = description
        self.comments = []
        self.user_id = user_id
        self.created_at = dt.now()
        self.updated_at = dt.now()

class Comment(Model):
    def __init__(self, id, title, content, user_id, date_posted):
        self.id = id
        self.content = content
        self.user_id = user_id
        self.date_posted = date_posted

class User(Model):
    def __init__(self, id, username, password, created_at, updated_at):
        self.id = id
        self.username = username
        self.password = password
        self.created_at = created_at
        self.updated_at = updated_at
