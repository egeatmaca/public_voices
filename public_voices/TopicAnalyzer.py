import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from models import Comment
from bson.objectid import ObjectId

class TopicAnalyzer:
    def __init__(self, topic_id) -> None:
        self.comments = Comment.find({'topic_id': topic_id})

    def get_word_counts(self):
        comment_contents = pd.Series(self.comments).apply(lambda x: x['content'])
        print(comment_contents)
        self.vectorizer = CountVectorizer(
            stop_words='english').fit(comment_contents)
        self.comment_vectors = pd.DataFrame(self.vectorizer.transform(
            comment_contents), columns=self.vectorizer.get_feature_names())
        print(self.comment_vectors)
        self.word_counts = self.comment_vectors.sum(axis=0).sort_values(ascending=False)
        print(self.word_counts)
        return self.word_counts

if __name__ == '__main__':
    ta = TopicAnalyzer('639614f151df2860db0fdbad')
    print(ta.get_word_counts())
