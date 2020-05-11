"""
script to build a {route_name : location} dictionary for all routes at a given location.
"""
import pymongo 
import pandas as pd 
import numpy as np
import random
import json 
import dns
import urllib.request
import os
import os.path
import re
from bs4 import BeautifulSoup
from datetime import datetime
import sys

from loguru import logger
from scipy.spatial.distance import cosine, pdist, squareform
import math

client = pymongo.MongoClient('mongodb+srv://eoghan:Ailbhe123@fypcluster-cqcwt.mongodb.net/test?retryWrites=true&w=majority')
route_link = 'https://www.ukclimbing.com/logbook/c.php?i={}'
graphs_link = 'https://www.ukclimbing.com/logbook/showgraph.php?id={}'
crag_link = 'https://www.ukclimbing.com/logbook/crag.php?id={}'
british_grades = ['D','HD','VD','HVD','S','HS','VS','HVS','E1','E2','E3','E4','E5','E6','E7','E8']

db = client.beta_db
comments = db.comments

all_comments = list(comments.find())

df = pd.DataFrame(all_comments)

try:
    with open('crag_lookup.json') as f:
          crag_lookup = json.load(f)
except:
    crag_lookup = dict()

crag_id = sys.argv[1]

def get_routes(crag_id) : 
    link = crag_link.format(crag_id)
    source = urllib.request.urlopen(link).read()
    soup = BeautifulSoup(source,'html.parser')

    location = soup.find('button', {'id': 'search_button'}).nextSibling.nextSibling.text

    table_rows = soup.find_all("tr")
    # parse the values for these rows and add them to a new list.

    rows = []
    for tr in table_rows[1:]:
        td = tr.find_all('td')
        info = [tr.text for tr in td] 
        info.extend([tr.get("data-id"),tr.nextSibling])
        rows.append(info + [''] * (8 - len(info)))

    df = pd.DataFrame(rows[2:], columns=["index", "name", "something1", "something2", "grade", "route_id", "ascents", "extra"])

    df['ascents'] = df['ascents'].apply(lambda x : np.nan if x is None else re.sub(r'<.*?>', r'',str(x)))

    df['ascents'] = df['ascents'].apply(lambda x : int(x) if str(x).isnumeric() else 0)

    df = df[df['ascents']<=6000]

    df['grade'] = df['grade'].apply(lambda string: re.split(r' +', str(string))[1] if any(grade in string for grade in british_grades) else np.nan)

    df = df.drop(['index', 'something1', 'something2','extra'], axis=1).dropna(subset = ['grade'])

    df['location'] = location
    
    return df

routes = get_routes(crag_id)
total = len(routes)
count = 1

def get_route_info(route_id):

    global count, total

    link = route_link.format(route_id)
    source = urllib.request.urlopen(link).read()
    soup = BeautifulSoup(source,'html.parser')
    route_info = soup.find_all("h1")[-1].text
    route_info = "_".join(route_info.split())
    
    print('{}/{} : {}'.format(count,total,route_info))
    count += 1
    
    return route_info

routes['route_info'] = routes['route_id'].map(get_route_info)

routes_crags = routes[['route_info', 'location']].set_index('route_info')

crag_lookup_extra = routes_crags.to_dict()['location']

crag_lookup.update(crag_lookup_extra)

with open('crag_lookup.json', 'w') as outfile:
        json.dump(crag_lookup, outfile)

df.route_info.map(lambda x: crag_lookup[x])




