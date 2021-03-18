from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import lxml.html as lh
import time
import requests
import os
import re

espn_data = {
  "mens" : {
    2021 : "https://fantasy.espn.com/tournament-challenge-bracket/2021/en/whopickedwhom",
    2019 : "http://fantasy.espn.com/tournament-challenge-bracket/2019/en/whopickedwhom",
    2018 : "https://web.archive.org/web/20190307213746/http://fantasy.espn.com/tournament-challenge-bracket/2018/en/whopickedwhom"
  },
  "womens" : {
    2021 : "https://fantasy.espn.com/tournament-challenge-bracket-women/2021/en/whopickedwhom",
    2019 : "http://fantasy.espn.com/tournament-challenge-bracket-women/2019/en/whopickedwhom",
    2018 : "https://web.archive.org/web/20190901044337/http://fantasy.espn.com/tournament-challenge-bracket-women/2018/en/whopickedwhom"
  }
}

def fetch_who_picked_data(year, gender, url):
  #todo code's all messed up
  # url = espn_data[gender][year]
  #Create a handle, page, to handle the contents of the website
  page = requests.get(url)
  #Store the contents of the website under doc
  doc = lh.fromstring(page.content)
  #Parse data that are stored between <tr>..</tr> of HTML
  tr_elements = doc.xpath('//tr')
  # print([len(T) for T in tr_elements[:12]])

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

      # fix so that data with – in it is not processed incorrectly
      split_data = data.split("-") 
      picked_percentage = split_data[-1]
      id = ''.join(split_data[0:-1])
      seed = re.search(r'\d+', id).group()
      team_name = id[len(seed):]
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
      #Increment i for the next column
      i+=1
  Dict={title:column for (title,column) in col}
  df=pd.DataFrame(Dict)
  df.head()
  df.to_csv("team_data/"+str(year)+"_"+gender+"_who_picked.csv", index=False)

def fetch_fivethirtyeight_data(year, file):
  page = requests.get("https://projects.fivethirtyeight.com/march-madness-api/"+str(year)+"/fivethirtyeight_ncaa_forecasts.csv")
  content = page.text
  with open(file, 'w') as f:
    f.write(content)

def check_if_data_exists(year, espn_data):
  current_path = os.path.dirname(__file__)
  five_thirty_eight_path = "../team_data/"+str(year)+"_fivethirtyeight_ncaa_forecasts.csv"
  five_thirty_eight_file = os.path.join(current_path, five_thirty_eight_path)
  if not os.path.exists(five_thirty_eight_file):
    print("Fetching 538 data from "+str(year)+".")
    fetch_fivethirtyeight_data(year, five_thirty_eight_file)
  else:
    print("538 data from "+str(year)+" exists.")
  if year in espn_data["mens"].keys():
    print("Data on team pick frequencies is available but not downloaded for "+str(year)+".  Downloading now.")
    espn_mens_path = "../team_data/"+str(year)+"_men_who_picked.csv"
    espn_mens_file = os.path.join(current_path, espn_mens_path)
    espn_womens_path = "../team_data/"+str(year)+"_women_who_picked.csv"
    espn_womens_file = os.path.join(current_path, espn_womens_path)
    if not os.path.exists(espn_mens_file):
      print("Fetching men's data for "+str(year)+".")
      fetch_who_picked_data(year, "mens", espn_data["mens"][year])
    if not os.path.exists(espn_womens_file):
      print("Fetching women's data for "+str(year)+".")
      fetch_who_picked_data(year, "womens", espn_data["womens"][year])
  else:
    print("Data on team pick frequencies is not available for "+str(year)+".")





check_if_data_exists(2021, espn_data)