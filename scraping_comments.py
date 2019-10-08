import pandas as pd
import urllib.request
import numpy as np
import os
import os.path
import re
from bs4 import BeautifulSoup
from datetime import datetime
import json

route_link = 'https://www.ukclimbing.com/logbook/c.php?i={}'
crag_link = 'https://www.ukclimbing.com/logbook/crag.php?id={}'
british_grades = ['HVD','VD','D','S','HS','VS','HVS','E1','E2','E3','E4','E5','E6','E7','E8']

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
        rows.append(info + [''] * (7 - len(info)))

    df = pd.DataFrame(rows[2:], columns=["index", "name", "something1", "something2", "grade", "route_id", "ascents", "extra"])

    df['ascents'] = df['ascents'].apply(lambda x : np.nan if x is None else re.sub(r'<.*?>', r'',str(x)))

    df['ascents'] = df['ascents'].apply(lambda x : int(x) if str(x).isnumeric() else 0)

    df = df[df['ascents']<=6000]

    df['grade'] = df['grade'].apply(lambda string: re.split(r' +', str(string))[1] if any(grade in string for grade in british_grades) else np.nan)

    df = df.drop(['index', 'something1', 'something2','extra'], axis=1).dropna(subset = ['grade'])

    df['location'] = location
    
    return df

def get_route_ascents(route_id) : 

    def correct_dates(date) :
        
        # ascents from this year have no year given ie. they take the form DD/MM
        # we use datetime to give the current year (so this should still work in future)
        if date[-1].isalpha() :
            return date+", "+str(datetime.now().year)

        return date
    
    link = route_link.format(route_id)
    source = urllib.request.urlopen(link).read()
    soup = BeautifulSoup(source,'html.parser')

    feedback = soup.find('div', attrs={'id':'feedback_div'})
    logs = soup.find('div', attrs={'id':'logbooks'})
    route_info = soup.find_all("h1")[-1].text
    route_info = "_".join(route_info.split())
    # beautiful soup makes it easy to find the table and store all of it rows
    table = logs.find('table')
    if table:
        table_rows = table.find_all('tr', attrs={'class':''})
            
        ascents = []
        
        for tr in table_rows:
            td = tr.find_all('td')
            #the climber id is contained in the link to their logbook so we need to store that
            link = tr.find('a').get('href')
            info = [tr.text for tr in td]
            #then we can use a regex to grab it
            climber_id = re.sub(r'.*=', r'', link)
            info.append(climber_id)
            ascents.append(info)
            
            
        # we can convert the ascents data we've just collected into a dataframe
        df = pd.DataFrame(ascents, columns=["name", "date", "style", "comment", "climber_id"])
        
        df['route_info'] = route_info
        df['beta'] = 0
        
        # finally we can fix the dates
        df['date'] = df["date"].apply(correct_dates)

        df = df.drop(['name','style'],axis =1)
    else: 
        df = pd.DataFrame()
    
    table = feedback.find('table')
    
    if table: 
        table_rows = table.find_all('tr')

        feedback = []

        for tr in table_rows:
            beta = tr.get('data-isbeta')
            if beta:
                text = tr.select('span[class*="comment comment_text_"]')[0].text
                date = tr.select('td[id*="datetext-"]')[0].text
                link = tr.find('a',href = True).get("href")
                climber_id = re.sub(r'.*=', r'', link)
                dic = {"beta": beta, "date": correct_dates(date), "climber_id": climber_id, 
                       "route_info": route_info,"comment": text}
                feedback.append(dic)
    else: 
        feedback = []
                
    return df.to_dict('records'), feedback
    
def get_comments(route_id):
    
    logs, feedbacks = get_route_ascents(route_id)

    output_dir = "comments/"

    for log in logs: 
        outfile_name = re.sub(" ", "_", log['route_info']+"_"+log['climber_id']+".json")

        with open(output_dir+outfile_name, "w") as outfile:
            json.dump(log, outfile)

    for feedback in feedbacks: 
        outfile_name = re.sub(" ", "_", feedback['route_info']+"_"+feedback['climber_id']+".json")

        if feedback['beta'] == "1": 
            output_dir = "feedback_w_beta/"
        else:
            output_dir  = "feedback_no_beta/"

        with open(output_dir+outfile_name, "w") as outfile:
            json.dump(feedback, outfile)


stanage_popular = get_routes(104)
for route_id in stanage_popular['route_id']:
    get_comments(route_id)

