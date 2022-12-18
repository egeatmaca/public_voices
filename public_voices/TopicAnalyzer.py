import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from wordcloud import WordCloud, STOPWORDS
import os
# from models import Comment
from public_voices.models import Comment

class TopicAnalyzer:
    def __init__(self, topic_id) -> None:
        self.topic_id = topic_id
        self.comments = pd.DataFrame(Comment.find({'topic_id': topic_id})).astype({'agree': 'int32'})
        self.plots_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static', 'images', 'plots')

    def get_agree_distribution(self, save=False):
        agree_value_counts = self.comments.agree.value_counts().sort_index()
        index_map = {-3: 'Totally disagree', -2: 'Disagree', -1: 'Kinda disagree', 0: 'Neutral', 1: 'Kinda agree', 2: 'Agree', 3: 'Totally agree'}
        agree_value_counts.index = agree_value_counts.index.map(index_map)
        sns.set_palette(sns.dark_palette("Green"))
        plot = sns.barplot(x=agree_value_counts.index, y=agree_value_counts.values)
        if save:
            plot.figure.savefig(os.path.join(self.plots_dir, f'topic{self.topic_id}_agree_dist.png'))
        return agree_value_counts, plot

    def get_word_counts(self, contents):
        vectorizer = CountVectorizer(
            stop_words='english').fit(contents)
        comment_vectors = pd.DataFrame(vectorizer.transform(
            contents).toarray(), columns=vectorizer.get_feature_names_out())
        word_counts = comment_vectors.sum(
            axis=0).sort_values(ascending=False)
        return word_counts

    def make_word_cloud(self, frequencies, save_file=None):
        word_cloud = WordCloud(
            background_color='white',
            max_words=200,
            max_font_size=40,
            scale=3,
            random_state=1
        ).generate_from_frequencies(frequencies)

        if save_file:
            word_cloud.to_file(save_file)

        return word_cloud

    def get_word_clouds(self):
        self.word_clouds = {}

        if not self.comments.empty:
            self.word_clouds['all'] = self.make_word_cloud(
                self.get_word_counts(self.comments.content), 
                save_file=os.path.join(self.plots_dir, f'topic{self.topic_id}.png'))
        
        agree_idx = self.comments.agree > 0
        if agree_idx.any():
            self.word_clouds['agree'] = self.make_word_cloud(
                self.get_word_counts(self.comments.loc[agree_idx, 'content']),
                    save_file=os.path.join(self.plots_dir, f'topic{self.topic_id}_agree.png')) 

        neutral_idx = self.comments.agree == 0
        if neutral_idx.any():
            self.word_clouds['neutral'] = self.make_word_cloud(
                self.get_word_counts(
                    self.comments.loc[neutral_idx, 'content']),
                save_file=os.path.join(self.plots_dir, f'topic{self.topic_id}_neutral.png'))

        disagree_idx = self.comments.agree < 0
        if disagree_idx.any():
            self.word_clouds['disagree'] = self.make_word_cloud(
                self.get_word_counts(
                    self.comments.loc[disagree_idx, 'content']),
                save_file=os.path.join(self.plots_dir, f'topic{self.topic_id}_disagree.png'))

        return self.word_clouds

    

if __name__ == '__main__':
    ta = TopicAnalyzer('639614f151df2860db0fdbad')
    print(ta.get_word_clouds())
