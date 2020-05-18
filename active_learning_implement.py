import pymongo 
import pandas as pd 
import numpy as np
import random
import json 
import dns

from active_learning_utils import EgalLearner

client = pymongo.MongoClient('mongodb+srv://eoghan:Ailbhe123@fypcluster-cqcwt.mongodb.net/test?retryWrites=true&w=majority')

db = client.beta_db
comments = db.comments

comment_list = list(comments.find())

df_total = pd.DataFrame(comment_list)
df_total = df_total.drop_duplicates(subset = ['comment'])

df_total.label = df_total[['label', 'pilot_1', 'pilot_2', 'pilot_3']].mean(axis = 1).round()

df_total = df_total.reset_index()
assert df_total.index.max() + 1 == df_total.shape[0]

learner = EgalLearner(df = df_total, labelled_pool_size = 'use_labels', classifier = 'random_forest',
                      rand_state = i, batch_size = 1)

for i in range(100):
    leaner.query_comments()

