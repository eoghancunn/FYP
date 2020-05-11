import pymongo
import json 
import config  
import sys

client = pymongo.MongoClient(config.MONGO_URI)
db = client.user_db
users = db.users

annotators_file = sys.argv[1]

with open(annotators_file) as annotators_json:
	json_data = annotators_json.read()
	annotators = json.loads(json_data)

users.insert_many(annotators)
