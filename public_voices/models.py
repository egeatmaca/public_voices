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

    @classmethod
    def insert_one(cls, model_obj):
        res = cls.collection.insert_one(model_obj.__dict__)
        return res

    @classmethod
    def find(cls, query):
        iter = cls.collection.find(query).sort('updated_at', -1)
        records = []
        for record in iter:
            records.append(record)
        return records

    @classmethod
    def find_one(cls, query):
        iter = cls.collection.find(query)
        for record in iter:
            return record
        return None
        
    @classmethod
    def update_one(cls, query, update):
        return cls.collection.update_one(query, update)

    @classmethod
    def delete_one(cls, query):
        return cls.collection.delete_one(query)

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

    def __init__(self, title, initial_comment, user_id, _id=None):
        self.id = _id
        self.title = title
        self.initial_comment = initial_comment
        # self.comments = []
        self.user_id = user_id
        self.created_at = dt.now()
        self.updated_at = dt.now()

    @classmethod
    def insert_one(cls, model_obj):
        res = Topic.collection.insert_one(model_obj.__dict__)
        _id = res.inserted_id
        model_obj.url = f'/topic/{_id}'
        model_obj.analyze_url = f'/analyze/{_id}'
        Topic.collection.update_one({'_id': _id}, {'$set': {'url': model_obj.url, 'analyze_url': model_obj.analyze_url}})
        return res


class Comment(Model):
    collection_name = 'comments'
    collection = db.comments

    def __init__(self, content, agree, topic_id, user_id, _id=None):
        self.id = _id
        self.content = content
        self.agree = agree
        self.topic_id = topic_id
        self.user_id = user_id
        self.created_at = dt.now()
        self.updated_at = dt.now()

    @classmethod
    def insert_one(cls, model_obj):
        res = Comment.collection.insert_one(model_obj.__dict__)
        # model_obj.id = res.inserted_id
        # model_obj.add_one_to_many_to(Topic, 'topic_id')
        return res


class User(Model):
    collection_name = 'users'
    collection = db.users

    def __init__(self, email, username):
        self.email = email
        self.username = username
        self.password = None
        self.created_at = dt.now()
        self.updated_at = dt.now()