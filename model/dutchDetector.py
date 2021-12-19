import tensorflow as tf
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import pickle

class DutchDetector:
    def __init__(self) -> None:
        self.model = tf.keras.models.load_model('recources/nn_trigram')
        self.train_min = pd.read_pickle('recources/trainmin.pkl')
        self.train_max = pd.read_pickle('recources/trainmax.pkl')
        file = open("recources/vocabulary.pkl", 'rb')
        vocab = pickle.load(file)
        file.close()
        vectorizer = CountVectorizer(analyzer='char',
                                    ngram_range=(3,3),
                                    vocabulary=vocab)

        self.feature_names = vectorizer.get_feature_names()

    def isDutch(self, url: str) -> bool:
        trigrams = self.vectorizer.fit_transform([url])
        features = pd.DataFrame(data=trigrams.toarray(), columns=self.feature_names)
        features = (features - self.train_min)/(self.train_max - self.train_min)
        return self.model.predict(features)[0][0] > 0.5

    def isDutchPercentage(self, url: str) -> float:
        trigrams = self.vectorizer.fit_transform([url])
        features = pd.DataFrame(data=trigrams.toarray(), columns=self.feature_names)
        features = (features - self.train_min)/(self.train_max - self.train_min)
        return self.model.predict(features)[0][0]
