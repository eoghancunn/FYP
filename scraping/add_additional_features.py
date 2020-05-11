import os
import re
import pandas as pd
import numpy as np
import scrapy
from loguru import logger
import json
import pymongo 

ukc_climbers_dir = '../data/raw/'
ukc_climbers_stats_dir = '../data/stats/'
graphs_link = 'https://www.ukclimbing.com/logbook/showgraph.php?id={}'
british_grades = ['M','D','ED1','HD','VD','HVD','MS','S','HS','MVS','VS','HVS','E1','E2','E3','E4','E5','E6','E7','E8']

client = pymongo.MongoClient('mongodb+srv://eoghan:Ailbhe123@fypcluster-cqcwt.mongodb.net/test?retryWrites=true&w=majority')
db = client.beta_db
comments = db.comments

comment_list = list(comments.find())
df = pd.DataFrame(comment_list)

def read_stats(climber_id, year) : 

    """
    gets the max grade, average grade and local area for the climber id and year

    Arguments:
    climber_id -- UKC climber ID of climber
    year -- the year of the stats

    Returns: 
    local area of climber
    average grade for the year
    max grade for the year

    """

    filename = '{}{}.csv'.format(ukc_climbers_stats_dir,climber_id)
    stats = pd.read_csv(filename).set_index('year')
    row = stats.loc[int(year)]
    return row['local_to'], row['avg_grade'], row['max_grade']

def get_grade(route_info):

    """
    extract the route grade from the route_info

    Arguments: 
    route_info -- the routes info as scraped from UKC

    Returns:
    grade of the route
    """

    route_info_split = re.split(r'_', str(route_info))
    grade = [value for value in route_info_split if value in british_grades]
    if len(grade) > 0:
        return grade[0]
    else:
        return np.nan

# load crag_lookup dict to get the location/crag for each route
with open('../crag_lookup.json') as f: 
        crag_lookup = json.load(f)


for _,row in df.iterrows():

    comment_id = row['_id']
    climber_id = row['climber_id']
    year = row['date'][-4:]
    route_info = row['route_info']

    try:
        local_to, avg_grade, max_grade = read_stats(climber_id,year)
    except:
        local_to, avg_grade, max_grade = np.nan, np.nan, np.nan

    location = crag_lookup[route_info]
    route_grade = get_grade(route_info)

    query = {"_id": comment_id}
    update = {"$set" : {"local_to" : local_to,
            "avg_grade_of_climber": avg_grade,
            "max_grade of climber": max_grade,
            "location": location, 
            "route_grade": route_grade}}

    comments.update_one(query,update)


