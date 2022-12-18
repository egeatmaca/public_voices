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
from wordcloud import WordCloud, STOPWORDS
import os

class TopicAnalyzer:
    def __init__(self, topic_id) -> None:
        self.topic_id = topic_id
        self.comments = Comment.find({'topic_id': topic_id})
        self.contents = pd.Series(self.comments).apply(lambda x: x['content'])
        self.word_clouds_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static', 'images', 'word_clouds')

    def get_word_counts(self):
        self.vectorizer = CountVectorizer(
            stop_words='english').fit(self.contents)
        self.comment_vectors = pd.DataFrame(self.vectorizer.transform(
            self.contents).toarray(), columns=self.vectorizer.get_feature_names_out())
        self.word_counts = self.comment_vectors.sum(axis=0).sort_values(ascending=False)
        return self.word_counts

    def get_word_cloud(self):
        self.vectorizer = TfidfVectorizer(
            stop_words='english').fit(self.contents)
        self.comment_vectors = pd.DataFrame(self.vectorizer.transform(
            self.contents).toarray(), columns=self.vectorizer.get_feature_names_out())
        self.words_tfidf = self.comment_vectors.sum(axis=0).sort_values(ascending=False)
        self.word_cloud = WordCloud(
            background_color='white',
            max_words=200,
            max_font_size=40,
            scale=3,
            random_state=1
        ).generate_from_frequencies(self.words_tfidf)
        self.word_cloud.to_file(os.path.join(self.word_clouds_dir, f'topic{self.topic_id}.png'))
        return self.word_cloud

if __name__ == '__main__':
    ta = TopicAnalyzer('639614f151df2860db0fdbad')
    print(ta.get_word_counts())
    print(ta.get_word_cloud().to_image())
