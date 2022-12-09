from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json
from datetime import datetime as dt

load_dotenv('.env')

client = MongoClient(os.environ.get('MONGODB_URI'))
db = client.public_voices


class Model:
    collection_name = 'topics'
    collection = db.topics

    @staticmethod
    def insert_one(model_obj):
        res = Model.collection.insert_one(model_obj.__dict__)
        return res

    @staticmethod
    def find(query):
        return Model.collection.find(query)

    @staticmethod
    def find_one(query):
        return Model.collection.find_one(query)

    @staticmethod
    def update_one(query, update):
        return Model.collection.update_one(query, update)

    @staticmethod
    def delete_one(query):
        return Model.collection.delete_one(query)

    def add_one_to_many_to(self, model_class, foreign_key):
        other = model_class.find_one({'_id': self.__dict__[foreign_key]})
        update_values = None
        if self.collection_name in other.keys():
            update_values = other[self.collection_name] + [self.id]
        else:
            update_values = [self.id]
        return model_class.update_one({'_id': self.__dict__[foreign_key]}, {'$push': {self.collection_name: update_values}})


class Topic(Model):
    collection_name = 'topics'
    collection = db.topics

    def __init__(self, title, description, user_id, _id=None, url=None, analyze_url=None):
        self.id = _id
        self.url = url
        self.analyze_url = analyze_url
        self.title = title
        self.description = description
        # self.comments = []
        self.user_id = user_id
        self.created_at = dt.now()
        self.updated_at = dt.now()

    @staticmethod
    def insert_one(model_obj):
        res = Topic.collection.insert_one(model_obj.__dict__)
        _id = res.inserted_id
        model_obj.url = f'/topic/{_id}'
        model_obj.analyze_url = f'/analyze/{_id}'
        Topic.collection.update_one({'_id': _id}, {'$set': {'url': model_obj.url, 'analyze_url': model_obj.analyze_url}})
        return res


class Comment(Model):
    collection_name = 'comments'
    collection = db.comments

    def __init__(self, content, topic_id, user_id, _id=None):
        self.id = _id
        self.content = content
        self.topic_id = topic_id
        self.user_id = user_id
        self.date_posted = dt.now()

    @staticmethod
    def insert_one(model_obj):
        res = Comment.collection.insert_one(model_obj.__dict__)
        model_obj.id = res.inserted_id
        # model_obj.add_one_to_many_to(Topic, 'topic_id')
        return res


class User(Model):
    def __init__(self, username, password, created_at, updated_at):
        self.username = username
        self.password = password
        self.created_at = created_at
        self.updated_at = updated_at
