import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import PCA
from wordcloud import WordCloud, STOPWORDS
from textblob import TextBlob
# from models import Comment
from public_voices.models import Comment

class TopicAnalyzer:
    def __init__(self, topic_id) -> None:
        self.topic_id = topic_id
        self.comments = pd.DataFrame(Comment.find({'topic_id': topic_id})).astype({'agree': 'int32'})

        vectorizer = CountVectorizer(
            stop_words='english').fit(self.comments.content)
        self.count_vectors = pd.DataFrame(vectorizer.transform(
            self.comments.content).toarray(), columns=vectorizer.get_feature_names_out())

        tfidf_vectorizer = TfidfVectorizer(
            stop_words='english').fit(self.comments.content)
        self.tfidf_vectors = pd.DataFrame(
            tfidf_vectorizer.transform(self.comments.content).toarray(),
            columns=tfidf_vectorizer.get_feature_names_out())

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
                self.count_vectors.sum(), 
                save_file=os.path.join(self.plots_dir, f'topic{self.topic_id}.png'))
        
        agree_idx = self.comments.agree > 0
        if agree_idx.any():
            self.word_clouds['agree'] = self.make_word_cloud(
                    self.count_vectors.loc[agree_idx].sum(),
                    save_file=os.path.join(self.plots_dir, f'topic{self.topic_id}_agree.png')) 

        neutral_idx = self.comments.agree == 0
        if neutral_idx.any():
            self.word_clouds['neutral'] = self.make_word_cloud(
                self.count_vectors.loc[neutral_idx].sum(),
                save_file=os.path.join(self.plots_dir, f'topic{self.topic_id}_neutral.png'))

        disagree_idx = self.comments.agree < 0
        if disagree_idx.any():
            self.word_clouds['disagree'] = self.make_word_cloud(
                self.count_vectors.loc[disagree_idx].sum(),
                save_file=os.path.join(self.plots_dir, f'topic{self.topic_id}_disagree.png'))

        return self.word_clouds

    
    def get_sentiment(self, text):
        sentiment = TextBlob(text).sentiment 
        return {'polarity': sentiment.polarity, 'subjectivity': sentiment.subjectivity}

    def analyze_sentiments(self):
        sentiments = self.comments.content.apply(self.get_sentiment)
        sentiments = pd.DataFrame(sentiments.tolist())

        sentiment_analysis = {}
        sentiment_analysis['all_sentiment_polarity'] = sentiments.polarity.mean()
        sentiment_analysis['all_sentiment_subjectivity'] = sentiments.subjectivity.mean(
        )
        sentiment_analysis['agree_sentiment_polarity'] = sentiments.loc[self.comments.agree > 0, 'polarity'].mean()
        sentiment_analysis['agree_sentiment_subjectivity'] = sentiments.loc[self.comments.agree > 0, 'subjectivity'].mean(
        )
        sentiment_analysis['neutral_sentiment_polarity'] = sentiments.loc[self.comments.agree == 0, 'polarity'].mean(
        )
        sentiment_analysis['neutral_sentiment_subjectivity'] = sentiments.loc[self.comments.agree == 0, 'subjectivity'].mean(
        )
        sentiment_analysis['disagree_sentiment_polarity'] = sentiments.loc[self.comments.agree < 0, 'polarity'].mean(
        )
        sentiment_analysis['disagree_sentiment_subjectivity'] = sentiments.loc[self.comments.agree < 0, 'subjectivity'].mean(
        )

        return sentiment_analysis

    def get_components(self):
        eig_vals, _ = np.linalg.eig(self.tfidf_vectors)
        n_components = np.where((np.cumsum(eig_vals) / np.sum(eig_vals)) > 0.8)[0] + 1

        pca = PCA(n_components=n_components)
        pca.fit(self.tfidf_vectors)
        components = pd.DataFrame(pca.components_)

        return components

    def map_features_to_components(self, components):
        # TODO
        return 

    def get_component_effects(self):
        # TODO
        return 

if __name__ == '__main__':
    ta = TopicAnalyzer('639614f151df2860db0fdbad')
    print(ta.get_word_clouds())
    print(ta.analyze_sentiments())
