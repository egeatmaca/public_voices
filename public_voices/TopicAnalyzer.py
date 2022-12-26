from pyspark.sql import SparkSession, functions as F, types as T
from pyspark.ml.feature import CountVectorizer, Tokenizer, StopWordsRemover, PCA, VectorAssembler, MinMaxScaler
from pyspark.ml.regression import LinearRegression
import numpy as np
import pandas as pd
import seaborn as sns
import os
from wordcloud import WordCloud
from textblob import TextBlob
# from models import Comment
from public_voices.models import Comment

spark = SparkSession.builder.appName('public_voices').getOrCreate()

class TopicAnalyzer:
    def __init__(self, topic_id) -> None:
        topic_comments = pd.Series(Comment.find({'topic_id': topic_id}, {'content': 1, 'agree': 1}))
        schema = T.StructType([
            T.StructField('content', T.StringType(), True),
            T.StructField('agree', T.StringType(), True)
        ])
        comments = spark \
            .createDataFrame(data=topic_comments, schema=schema) \
            .withColumn('agree', F.col('agree').cast(T.IntegerType()))

        self.topic_id = topic_id
        self.comments = comments
        self.word_counts = self.extract_word_counts(comments)
        self.plots_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static', 'images', 'plots')

    def extract_word_counts(self, comments):
        tokenizer = Tokenizer(inputCol='content', outputCol='words')
        comments = tokenizer.transform(comments)

        remover = StopWordsRemover(inputCol='words', outputCol='filtered')
        comments = remover.transform(comments)

        cv = CountVectorizer(inputCol='filtered', outputCol='vectors')
        cv_model = cv.fit(comments)
        cv_results = cv_model.transform(comments)
        word_counts_schema = T.StructType([
            T.StructField(word, T.FloatType(), True) for word in cv_model.vocabulary
        ])
        word_counts = cv_results.select('vectors').rdd.map(
            lambda x: x['vectors'].toArray().tolist()).toDF(schema=word_counts_schema)
        
        return word_counts 


    def get_agree_distribution(self, save=False):
        agree_value_counts = self.comments.groupby('agree').count().toPandas().set_index('agree')['count']
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

        comments_temp = self.comments.withColumn('pseudo_id', F.monotonically_increasing_id())
        word_counts_temp = self.word_counts.withColumn('pseudo_id', F.monotonically_increasing_id())
        word_counts_wagree = word_counts_temp.join(
                                comments_temp.select('pseudo_id', 'agree').withColumnRenamed(
                                    'agree', 'agree_points__'), 
                                on='pseudo_id', how='left'
                            ).drop('pseudo_id')
        word_col_sums = [F.sum(c).alias(c) for c in word_counts_wagree.columns if c != 'agree_points__']

        if self.comments.rdd.count() > 0:
            frequencies = word_counts_wagree.select(word_col_sums).toPandas().iloc[0].to_dict() 

            self.word_clouds['all'] = self.make_word_cloud(frequencies,
                save_file=os.path.join(self.plots_dir, f'topic{self.topic_id}.png'))
        
        word_counts_agree = word_counts_wagree.filter(word_counts_wagree.agree_points__ > 0)
        if word_counts_agree.rdd.count() > 0:
            frequencies = word_counts_agree.select(
                word_col_sums).toPandas().iloc[0].to_dict()

            self.word_clouds['agree'] = self.make_word_cloud(frequencies,
                    save_file=os.path.join(self.plots_dir, f'topic{self.topic_id}_agree.png')) 

        word_counts_neutral = word_counts_wagree.filter(
            word_counts_wagree.agree_points__ == 0)
        if word_counts_neutral.rdd.count() > 0:
            frequencies = word_counts_neutral.select(
                word_col_sums).toPandas().iloc[0].to_dict()

            self.word_clouds['neutral'] = self.make_word_cloud(frequencies,
                save_file=os.path.join(self.plots_dir, f'topic{self.topic_id}_neutral.png'))

        word_counts_disagree = word_counts_wagree.filter(
            word_counts_wagree.agree_points__ < 0)
        if word_counts_disagree.rdd.count() > 0:
            frequencies = word_counts_disagree.select(
                word_col_sums).toPandas().iloc[0].to_dict()

            self.word_clouds['disagree'] = self.make_word_cloud(frequencies,
                save_file=os.path.join(self.plots_dir, f'topic{self.topic_id}_disagree.png'))

        return self.word_clouds

    
    def get_sentiment(self, comment):
        sentiment = TextBlob(comment.content).sentiment 
        return {'polarity': sentiment.polarity, 'subjectivity': sentiment.subjectivity, 'agree': comment.agree}

    def analyze_sentiments(self):
        sentiments = spark.sparkContext.parallelize(
            self.comments.toPandas().apply(self.get_sentiment, axis=1).tolist())
        
        sentiment_analysis = {}

        sentiment_analysis['all_sentiment_polarity'] = sentiments.map(lambda x: x['polarity']).mean()
        sentiment_analysis['all_sentiment_subjectivity'] = sentiments.map(lambda x: x['subjectivity']).mean()
        
        agree_sentiments = sentiments.filter(lambda x: x['agree'] > 0)
        sentiment_analysis['agree_sentiment_polarity'] = agree_sentiments.map(
            lambda x: x['polarity']).mean()
        sentiment_analysis['agree_sentiment_subjectivity'] = agree_sentiments.map(
            lambda x: x['subjectivity']).mean()
        
        neutral_sentiments = sentiments.filter(lambda x: x['agree'] == 0)
        sentiment_analysis['neutral_sentiment_polarity'] = neutral_sentiments.map(
            lambda x: x['polarity']).mean()
        sentiment_analysis['neutral_sentiment_subjectivity'] = neutral_sentiments.map(
            lambda x: x['subjectivity']).mean()

        disagree_sentiments = sentiments.filter(lambda x: x['agree'] < 0)      
        sentiment_analysis['disagree_sentiment_polarity'] = disagree_sentiments.map(
            lambda x: x['polarity']).mean()
        sentiment_analysis['disagree_sentiment_subjectivity'] = disagree_sentiments.map(
            lambda x: x['subjectivity']).mean()

        return sentiment_analysis

    def apply_pca(self):
        k = len(self.word_counts.columns)
        vecAssembler = VectorAssembler(inputCols=self.word_counts.columns, outputCol='features')
        word_counts = vecAssembler.transform(self.word_counts)

        pca = PCA(k=k, inputCol='features', outputCol='pca_features')
        pca_model = pca.fit(word_counts)
        word_counts = pca_model.transform(word_counts)
        
        pca_array = np.array(
            word_counts.rdd.map(
                lambda x: x['pca_features'].toArray().tolist()
            ).collect()
        )

        n_components = np.where(
            pca_model.explainedVariance.toArray().cumsum() >= 0.8)[0][0] + 1
        
        
        self.df_pca = spark.createDataFrame(pca_array[:, :n_components].tolist())

        return self.df_pca

    def map_components_to_features(self):
        # Scale df_pca
        vec_assembler = VectorAssembler(inputCols=self.df_pca.columns, outputCol='features')
        df_pca = vec_assembler.transform(self.df_pca)
        scaler = MinMaxScaler(inputCol='features', outputCol='scaled_features')
        self.df_pca_scaled = scaler.fit(df_pca).transform(df_pca)

        # Scale word_counts
        vec_assembler = VectorAssembler(inputCols=self.word_counts.columns, outputCol='features')
        word_counts = vec_assembler.transform(self.word_counts)
        scaler = MinMaxScaler(inputCol='features', outputCol='scaled_features')
        word_counts_scaled = scaler.fit(word_counts).transform(word_counts)
        word_counts_scaled = word_counts_scaled.rdd.map(
                lambda x: [float(y) for y in x['scaled_features']]
            ).toDF(self.word_counts.columns)

        df_model = self.df_pca_scaled \
            .withColumn('pseudo_id', F.monotonically_increasing_id()) \
            .join(
                word_counts_scaled.withColumn(
                    'pseudo_id', F.monotonically_increasing_id()),
                on='pseudo_id', how='left'
            )

        word_coefs = {}
        for word in self.word_counts.columns:
            if word == 'features':
                continue

            lr = LinearRegression(featuresCol='scaled_features', labelCol=word)
            lr_model = lr.fit(df_model)
            word_coefs[word] = lr_model.coefficients.toArray().tolist()

        self.word_coefs = pd.DataFrame(word_coefs).T

        self.component_features = {}
        for component in self.word_coefs.columns:
            self.component_features[component] = self.word_coefs.index[self.word_coefs[component] > 0.1].tolist()
        
        return self.component_features

    def get_component_effects(self):
        vec_assembler = VectorAssembler(inputCols=['agree'], outputCol='agree_vec')
        comments_agree_vec = vec_assembler.transform(self.comments)

        scaler = MinMaxScaler(inputCol='agree_vec', outputCol='agree_scaled')
        comments_agree_scaled = scaler.fit(comments_agree_vec).transform(comments_agree_vec)
        comments_agree_scaled = comments_agree_scaled.rdd.map(
                lambda x: [float(x['agree_scaled'].toArray()[0])]
            ).toDF(
                T.StructType([
                    T.StructField('agree_scaled', T.FloatType(), True)
                ])
            )

        df_model = self.df_pca_scaled.withColumn('pseudo_id', F.monotonically_increasing_id()).join(
                comments_agree_scaled.select('agree_scaled').withColumn('pseudo_id', F.monotonically_increasing_id()),
            on='pseudo_id', how='left')

        df_model.show() 

        lr = LinearRegression(featuresCol='scaled_features', labelCol='agree_scaled')
        lr_model = lr.fit(df_model)
        coefs = lr_model.coefficients.toArray().tolist()

        return pd.Series(coefs)

if __name__ == '__main__':
    ta = TopicAnalyzer('639614f151df2860db0fdbad')
    print(ta.get_word_clouds())
    print(ta.analyze_sentiments())
    print(ta.apply_pca())
    print(ta.map_components_to_features())
    print(ta.get_component_effects())
