import os
import pandas as pd
import urllib.request
import numpy as np
from bs4 import BeautifulSoup
import scrapy
from loguru import logger
from scrapy.crawler import CrawlerProcess
import pymongo 

ukc_climbers_dir = '../data/raw/'
ukc_climbers_stats_dir = '../data/stats/'
graphs_link = 'https://www.ukclimbing.com/logbook/showgraph.php?id={}'
british_grades = ['S','HS','VS','HVS','E1','E2','E3','E4','E5','E6','E7','E8']

client = pymongo.MongoClient('mongodb+srv://eoghan:Ailbhe123@fypcluster-cqcwt.mongodb.net/test?retryWrites=true&w=majority')
db = client.beta_db
comments = db.comments

comment_list = list(comments.find())

df = pd.DataFrame(comment_list)

class UKCSpider(scrapy.Spider):
    
    name = "ukc_spider"

    def start_requests(self):
        
        for climber_id in df['climber_id'].values:
            
            filename = '{}{}.html'.format(ukc_climbers_dir,climber_id)
            
            if not(os.path.isfile(filename)):
                yield scrapy.Request(
                    url=graphs_link.format(climber_id),
                    callback=self.parse,
                    meta={'climber_id': climber_id, 'filename': filename},
                )

    def parse(self, response):
        filename = response.meta['filename']
        with open(filename, 'w') as f:
            f.write(response.text)
        self.log('Saved file %s' % filename)
        
process = CrawlerProcess()

process.crawl(UKCSpider)
process.start() 

def produce_stats_for_climber(climber_id) : 
        logger.debug('producing stats for climber {}'.format(climber_id))

        filename = '{}{}.html'.format(ukc_climbers_dir,climber_id)
        try:
            f=open(filename, "r")
            source = f.read()
            soup = BeautifulSoup(source,'html.parser')
            # the crag (location) that a climber visits most is the first text field found after the divider with the id 'crag' 
            local_to = soup.find("div", {"id": "crag"}).find('a').text

            # average and max grades are stored in the table that is accessed below. 
            # 'gradetype2' is there title for trad climbing and 'British' indicates the british grading system. 
            table = soup.find("div", {"id": "gradetype2"}).find("h5", string = 'British').nextSibling.nextSibling
            rows = table.find_all('tr')

            stats = []

            for row in rows[1:]: 
                tds = row.find_all('td')
                stats.append([tds[0].string, tds[-2].string, tds[-1].string, local_to])

            df = pd.DataFrame(stats, columns = ['year', 'avg_grade', 'max_grade', 'local_to']).set_index('year')
            df.to_csv("{}{}.csv".format(ukc_climbers_stats_dir,climber_id))
            
        except:
            logger.info('no climber data for {}'.format(climber_id))
            
        return 

climber_ids = df['climber_id'].unique()
len(climber_ids)

for climber_id in climber_ids:
    produce_stats_for_climber(climber_id)




