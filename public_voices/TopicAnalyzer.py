import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import PCA 
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import statsmodels.api as sm
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
        self.df_count = pd.DataFrame(vectorizer.transform(
            self.comments.content).toarray(), columns=vectorizer.get_feature_names_out())

        tfidf_vectorizer = TfidfVectorizer(
            stop_words='english').fit(self.comments.content)
        self.df_tfidf = pd.DataFrame(
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
                self.df_count.sum(), 
                save_file=os.path.join(self.plots_dir, f'topic{self.topic_id}.png'))
        
        agree_idx = self.comments.agree > 0
        if agree_idx.any():
            self.word_clouds['agree'] = self.make_word_cloud(
                    self.df_count.loc[agree_idx].sum(),
                    save_file=os.path.join(self.plots_dir, f'topic{self.topic_id}_agree.png')) 

        neutral_idx = self.comments.agree == 0
        if neutral_idx.any():
            self.word_clouds['neutral'] = self.make_word_cloud(
                self.df_count.loc[neutral_idx].sum(),
                save_file=os.path.join(self.plots_dir, f'topic{self.topic_id}_neutral.png'))

        disagree_idx = self.comments.agree < 0
        if disagree_idx.any():
            self.word_clouds['disagree'] = self.make_word_cloud(
                self.df_count.loc[disagree_idx].sum(),
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

    def apply_pca(self):
        pca = PCA()
        pca.fit(self.df_tfidf)

        n_components = np.where(pca.explained_variance_ratio_.cumsum() >= 0.8)[0][0] + 1
        
        self.df_pca = pd.DataFrame(pca.transform(self.df_tfidf)[:, :n_components])

        return self.df_pca

    def map_components_to_features(self):
        self.scaler = MinMaxScaler()
        self.df_tfidf_scaled = pd.DataFrame(self.scaler.fit_transform(self.df_tfidf), columns=self.df_tfidf.columns)
        self.df_pca_scaled = pd.DataFrame(self.scaler.fit_transform(self.df_pca), columns=self.df_pca.columns)

        word_coefs = {}
        for word in self.df_tfidf_scaled.columns:
            model = sm.OLS(self.df_tfidf_scaled[word], self.df_pca_scaled).fit()
            word_coefs[word] = model.params

        self.word_coefs = pd.DataFrame(word_coefs).T

        self.component_features = {}
        for component in self.word_coefs.columns:
            self.component_features[component] = self.word_coefs.index[self.word_coefs[component] > 0.5].tolist()
        
        return self.component_features

    def get_component_effects(self):
        self.agree_scaled = self.scaler.fit_transform(self.comments[['agree']])
        model = sm.OLS(self.agree_scaled, self.df_pca_scaled).fit()
        return model.params

if __name__ == '__main__':
    ta = TopicAnalyzer('639614f151df2860db0fdbad')
    print(ta.get_word_clouds())
    print(ta.analyze_sentiments())
    print(ta.apply_pca())
    print(ta.map_components_to_features())
    print(ta.get_component_effects())
