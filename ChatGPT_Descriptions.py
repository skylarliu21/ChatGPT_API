# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 11:19:30 2024

@author: sliu
"""

import time
import requests
import pandas as pd 
from sqlalchemy import create_engine
 
# set api headers and parameters
headers = {"Content-Type": "application/json", "Authorization": "API Key"}

# create output
output = list() 

# import item titles minus previous data
engine = create_engine('SQL Database', echo = False)
items = pd.read_sql_table('Table', con = engine)
ids = items[["ProdID", "Long Description"]]
previous_df = pd.read_sql_table('Table', con = engine)
outer = items.merge(previous_df, on = "ProdID", how='outer', indicator=True) 
title = outer[(outer._merge == 'left_only')].drop('_merge', axis = 1)["Long Description"].tolist()
 
for i in title[:200]: 
 
    nextrow = False 
    while not nextrow: 
         
        # connect to chatGPT api
        try:
            resp = requests.post("https://api.openai.com/v1/chat/completions",headers=headers,json={"model": "gpt-3.5-turbo",
                 "messages": [{"role": "user", "content": "can you provide me with a nice description for "+i+"? Don't use full Upper case words please"}],
                 "temperature": 0.7})
            gpt_page = resp.json()
            description = gpt_page.get("choices")[0].get("message").get("content")
        except Exception:
            print(Exception)
            time.sleep(10)
                 
        row = {} 
        row['Input Title'] = i 
        print(i)
        row['Description'] = description
        output.append(row) 
        nextrow = True
        
        time.sleep(20) 
 
output_df = pd.DataFrame(output) 
# remove repetitive phrase
output_df["Description"] = output_df["Description"].str.replace('is a captivating fragrance that ', '')
output_df = ids.merge(output_df, left_on="Long Description", right_on="Input Title").drop(columns = ["Long Description", "Input Title"])

engine = create_engine('SQL Database', echo = False)
output_df.to_sql('Table', engine, if_exists = 'append', index = False)