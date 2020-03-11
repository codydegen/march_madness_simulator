from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import lxml.html as lh
import time
import requests
import os
import re

espn_2019_men = {
  "year": 2019,
  "gender": "men",
  "url": "http://fantasy.espn.com/tournament-challenge-bracket/2019/en/whopickedwhom"
}

espn_2019_women = {
  "year": 2019,
  "gender": "women",
  "url": "http://fantasy.espn.com/tournament-challenge-bracket-women/2019/en/whopickedwhom"
}

espn_2018_men = {
  "year": 2018,
  "gender": "men",
  "url": "https://web.archive.org/web/20190307213746/http://fantasy.espn.com/tournament-challenge-bracket/2018/en/whopickedwhom"
}

espn_2018_women = {
  "year": 2018,
  "gender": "women",
  "url": "https://web.archive.org/web/20190901044337/http://fantasy.espn.com/tournament-challenge-bracket-women/2018/en/whopickedwhom#"
}

def get_who_picked(dataset):
  #Create a handle, page, to handle the contents of the website
  page = requests.get(dataset["url"])
  #Store the contents of the website under doc
  doc = lh.fromstring(page.content)
  #Parse data that are stored between <tr>..</tr> of HTML
  tr_elements = doc.xpath('//tr')
  print([len(T) for T in tr_elements[:12]])

  tr_elements = doc.xpath('//tr')
  #Create empty list
  col = []
  i = 0
  # start by adding rows for team seed and name
  col.append(("team_seed",[]))
  col.append(("team_name",[]))

  #For each other row, store each first element (header) and an empty listhello like it
  for t in tr_elements[0]:
    i += 1
    name = t.text_content()
    # print '%d:"%s"'%(i,name)
    col.append((name,[]))

  for j in range(1,len(tr_elements)):
    #T is our j'th row
    T = tr_elements[j]
    
    #If row is not of size 6, the //tr data is not from our table 
    if len(T) != 6:
      break
    
    i = 0
    
    #Iterate through each element of the row
    for t in T.iterchildren():
      data = t.text_content() 
      picked_percentage = data.split("-")[1]
      id = data.split("-")[0]
      seed = re.search(r'\d+', id).group()
      team_name = id[len(seed):]
      data_name = seed+","+team_name
      if team_name not in col[1][1]:
        # col[i+1]
        col[0][1].append(seed)
        col[1][1].append(team_name)
        col[i+2][1].append(picked_percentage)
        pass
      else:
        index = col[1][1].index(team_name)
        # col[0][1].insert(index, seed)
        col[i+2][1].insert(index, picked_percentage)
      # if i>0:
      # #Convert any numerical value to integers
        # try:
          # data=int(data)
        # except:
          # pass
      # #Append the data to the empty list of the i'th column
      # col[i][1].append(data)
      # #Increment i for the next column
      i+=1
  Dict={title:column for (title,column) in col}
  df=pd.DataFrame(Dict)
  df.head()

  df.to_csv("data/"+str(dataset["year"])+"_"+dataset["gender"]+"_who_picked.csv", index=False)

get_who_picked(espn_2018_men)
get_who_picked(espn_2019_women)
get_who_picked(espn_2018_women)