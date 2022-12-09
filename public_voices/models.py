from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime as dt

load_dotenv('.env')

client = MongoClient(os.environ.get('MONGODB_URI'))
db = client.public_voices


class Model:
    collection_name = 'topics'
    collection = db.topics

    @staticmethod
    def insert_one(model_obj):
        return Model.collection.insert_one(model_obj.__dict__)

    @staticmethod
    def find(filter_):
        return Model.collection.find(filter_)

    @staticmethod
    def find_one(filter_):
        return Model.collection.find_one(filter_)

    @staticmethod
    def update_one(filter_, update):
        return Model.collection.update_one(filter_, update)

    @staticmethod
    def delete_one(filter_):
        return Model.collection.delete_one(filter_)

    def add_one_to_many_to(self, model_class, foreign_key):
        other = model_class.find_one({'id': self.__dict__[foreign_key]})
        update_values = None
        if self.collection_name in other.keys():
            update_values = other[self.collection_name] + [self.id]
        else:
            update_values = [self.id]
        return model_class.update_one({'id': self.__dict__[foreign_key]}, {'$push': {self.collection_name: update_values}})


class Topic(Model):
    collection_name = 'topics'
    collection = db.topics

    def __init__(self, id, title, description, user_id):
        self.id = id
        self.url = f'/topic/{id}'
        self.analyze_url = f'/analyze/{id}'
        self.title = title
        self.description = description
        self.comments = []
        self.user_id = user_id
        self.created_at = dt.now()
        self.updated_at = dt.now()


class Comment(Model):
    collection_name = 'comments'
    collection = db.comments

    def __init__(self, id, content, topic_id, user_id):
        self.id = id
        self.content = content
        self.topic_id = topic_id
        self.user_id = user_id
        self.date_posted = dt.now()

    @staticmethod
    def insert_one(model_obj):
        res = Comment.collection.insert_one(model_obj.__dict__)
        model_obj.add_one_to_many_to(Topic, 'topic_id')
        return res


class User(Model):
    def __init__(self, id, username, password, created_at, updated_at):
        self.id = id
        self.username = username
        self.password = password
        self.created_at = created_at
        self.updated_at = updated_at
