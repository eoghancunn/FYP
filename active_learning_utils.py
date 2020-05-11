import pandas as pd 
import numpy as np
import random
import json 

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import pairwise
from sklearn import metrics
from sklearn import svm

from sklearn.metrics import pairwise_distances
from scipy.spatial.distance import cosine, pdist, squareform
import math


class ActiveLearner:

    def __init__(self, df, labelled_pool_size, classifier, rand_state, batch_size, sampling_func):
        
        self.df = df
        self.sampling_func = sampling_func
        self.rand_state = rand_state
        self.batch_size = batch_size
        self._setup(labelled_pool_size, classifier)

    def _setup(self, labelled_pool_size, classifier):

        clfs  = {"svm" : svm.SVC(kernel='linear', probability=True, random_state= self.rand_state),
                "random_forest" : RandomForestClassifier(n_estimators=50, random_state= self.rand_state)}
        self.clf = clfs[classifier]
        
        if labelled_pool_size == 'use_labels':
            # use the labelled comments for the labelled pool 
            labelled_comments = self.df[~self.df['label'].isna()]
            self.labelled = list(labelled_comments.index)
        else:
            # choose k positive comments and k negatice comments random to fill random pool
            k = int(labelled_pool_size/2)
            pos = self.df[self.df.label == 1].sample(k, random_state = self.rand_state).index
            neg = self.df[self.df.label == 0].sample(k, random_state = self.rand_state).index
            self.labelled = list(pos) + list(neg)

        tfidf_vect = TfidfVectorizer(ngram_range = (1,3), stop_words = 'english')
        self.comment_vects = tfidf_vect.fit_transform(self.df.comment)

    def predict(self):

        X_train_vect = self.comment_vects[self.labelled]
        X_test_vect = self.comment_vects

        y_train = self.df.iloc[self.labelled].label
        y_test = self.df.label

        self.clf.fit(X_train_vect.toarray(), y_train) 
        pred = self.clf.predict(X_test_vect.toarray())
        perf = metrics.balanced_accuracy_score(y_test, pred)

        return perf

    def iterate(self): 
        
        df_un_labelled = self.df.iloc[~self.df.index.isin(self.labelled)]
        df_un_labelled['informative'] = df_un_labelled.index.map(lambda x:
                self.sampling_func(self.comment_vects[x].A, self.clf))
        df_un_labelled = df_un_labelled.sort_values(by = 'informative')

        self.labelled = self.labelled + list(df_un_labelled.iloc[:self.batch_size].index)

        return self.labelled[-self.batch_size:]
    
    def query_comments(self):

        queried_comment_index = self.iterate()
        queiried_comments = self.df.loc[queried_comment_index]
        for comment in queried_comments:
            _query(comment._id)


    def _query(self, comment_id):

        query = {"_id" : comment_id}
        update ={"$set" : {"queried": 1}}
        result = comments.update_one(query,update)
        success = result.matched_count > 0

        return success

class EgalLearner(ActiveLearner):
    
    def __init__(self, df, labelled_pool_size, classifier, rand_state, batch_size, sampling_func = None):
        super().__init__(df, labelled_pool_size, classifier, rand_state, batch_size, sampling_func)
        
    def _setup(self, labelled_pool_size, classifier):

        super()._setup(labelled_pool_size, classifier)

        dists = 1 - pairwise_distances(self.comment_vects, metric = 'cosine')
        self.df_sim = pd.DataFrame(dists, 
                                     columns=self.df.index, 
                                     index=self.df.index)
        self.alpha = 1.5 * dists.mean()
        self.beta = 0.5

    def iterate(self):

        num_candidates = math.ceil((len(self.df) - len(self.labelled)) * self.beta)
    
        df_un_labelled = self.df.loc[~self.df.index.isin(self.labelled)]
        df_un_labelled['diversity'] = df_un_labelled.index.map(lambda x: diversity(self.df_sim.iloc[x], self.labelled))
        
        candidates = df_un_labelled.sort_values(by = 'diversity', ascending = True)[:num_candidates]
        candidates['density'] = candidates.index.map(lambda x: density(self.df_sim.iloc[x],self.alpha))
        candidates = candidates.sort_values(by = 'density', ascending = False)
        
        self.labelled = self.labelled + list(candidates.iloc[:self.batch_size].index)

        return self.labelled[-self.batch_size:]


    

def uncertainty_sampling(comment_vects, clf):
    
    """
    Return the uncertainty of the clasification of each of the 
    comments in the comment_vects array by the classifier clf

    Keyword arguments:
    comment_vects -- array of vectorized comments

    clf -- sklearn classifier for classification
    """

    prob = clf.predict_proba(comment_vects)[:,1]
    uncertainty = abs(prob - 0.5)
    
    return uncertainty

def random_sampling(comment_vects, clf):

    """
    Returns a random value to allow for random sampling
    """

    return random.randrange(1000)

def diversity(sim_x, labelled): 

    """
    Return the egal defined diversity of x

    Keyword arguments:
    sim_x -- the similarity of all samples to x
                ie. the xth column/row of the similarity matrix
    labelled -- the indices of all labelled samples
    """

    sim_to_labelled = sim_x.iloc[labelled]
    diversity = sim_to_labelled.max()
    return diversity


def density(sim_x, alpha):

    """
    Return the egal defined density of x

    Keyword arguments:
    sim_x -- the of all examples to x 
                ie. the xth column/row of the similarity matrix
    alpha -- the neightbourhood radius
    """

    neighbourhood = sim_x[sim_x > alpha] # filter within neighbourhood
    density = neighbourhood.sum() 
    density -= 1 # remove similarity to self. 
    return density

