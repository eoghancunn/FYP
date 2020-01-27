import pymongo 
import os 
import json
import pandas as pd

MONGO_URI = os.environ.get('MONGO_URI')

client = pymongo.MongoClient('mongodb+srv://eoghan:Ailbhe123@fypcluster-cqcwt.mongodb.net/test?retryWrites=true&w=majority')

beta_dir = 'feedback_no_beta'
files = []

for (dirpath, dirnames, filenames) in os.walk(beta_dir): 
    for f in filenames:
        files.append(os.path.join(dirpath,f))

samples = []

for log in files:
    with open(log) as json_file:
        samples.append(json.load(json_file))

db = client.beta_db
comments = db.comments

comments.insert_many(samples)

print(db.list_collection_names())
