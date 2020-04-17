from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import lxml.html as lh
import time
import requests
import os
import json

class TopLevelScrape:

  def findMissing(self, path):
    i = 1
    unused = []
    discontinuity = False
    while discontinuity == False:
      if os.path.exists(path+"/resultsPgi"+str(i)+".json") == False:
        unused.append(i)
        print("missing sheet found: ", i)
        if i-1 in unused:
          discontinuity = True
      i+=1
    return unused

  def pageExtract(self, content):
    soup = BeautifulSoup(content, 'html.parser')
    result = soup.select('div#groupTableWrapper')[0].select('tbody')[0] # main table
    i = 1
    time.sleep(1)
    ranks=[] #Rank
    # entries=[] #Ranks
    names=[] #Ranks
    links=[] #Ranks
    r64s=[] #Ranks
    r32s=[] #Ranks
    r16s=[] #Ranks
    r8s=[] #Ranks
    r4s=[] #Ranks
    r2s=[] #Ranks
    champs=[] #List to store price of the product
    totals=[] #List to store rating of the product
    percentiles=[] #List to store rating of the product
    for tr in result.findAll('tr'):
      rank = tr.find('td', attrs={'class':'rank'}).text
      entry = tr.find('a', attrs={'class':'entry'})
      name = entry.text
      bracketlink = entry.attrs['href']
      r64 = tr.find('td', attrs={'class':'period_0'}).text
      r32 = tr.find('td', attrs={'class':'period_1'}).text
      r16 = tr.find('td', attrs={'class':'period_2'}).text
      r8 = tr.find('td', attrs={'class':'period_3'}).text
      r4 = tr.find('td', attrs={'class':'period_4'}).text
      r2 = tr.find('td', attrs={'class':'period_5'}).text
      champ = tr.find('td', attrs={'class':'champ'}).text
      total = tr.find('td', attrs={'class':'total'}).text
      percentile = tr.find('td', attrs={'class':'percentile'}).text
      i+=1
      ranks.append(rank)
      names.append(name)
      links.append(bracketlink)
      r64s.append(r64)
      r32s.append(r32)
      r16s.append(r16)
      r8s.append(r8)
      r4s.append(r4)
      r2s.append(r2)
      champs.append(champ)
      totals.append(total)
      percentiles.append(percentile)
    data = {'Rank':ranks,'Names':names,'Link':links,'R64':r64s,'R32':r32s,'R16':r16s,'R8':r8s,'R4':r4s,'R2':r2s,'Champ Pick':champs,'Total':totals,'Percentile':percentiles}
    df = pd.DataFrame(data, columns= ['Rank','Names','Link','R64','R32','R16','R8','R4','R2','Champ Pick','Total','Percentile']) 
    return df

  def nextPage(self, driver):
    next_button = driver.find_element_by_css_selector('a.nextPage')
    next_button.click()
    time.sleep(2)
    pageNum = driver.find_element_by_css_selector('strong.selected')
    return str(pageNum.text)

  def gotoPage(self, driver, pn):
    try:
      tb = driver.find_element_by_xpath("//a[@data-start='"+str((pn-1)*50)+"']")
    except:
      # finish this
      print("oops")
      found = False
      while found == False:
        tblist = driver.find_elements_by_css_selector("a.navigationLink.pageNumber")
        try:
          maxPage = int(tblist[-1].text)
        except IndexError as err:
          print('Index error, waiting: ', err)
          time.sleep(5)
          tblist = driver.find_elements_by_css_selector("a.navigationLink.pageNumber")
          maxPage = int(tblist[-1].text)
          pass
        minPage = int(tblist[0].text)
        if pn > maxPage:
          tblist[-1].click()
          time.sleep(3)
        elif pn < minPage:
          tblist[0].click()
          time.sleep(3)
        else:
          for i in tblist:
            if pn == int(i.text):
              tb = i
              found = True
    tbpn = tb.text
    tb.click()
    time.sleep(1)
    return str(tbpn)

  def main(self, PROXY, dataset):
    webdriver.DesiredCapabilities.CHROME['proxy']={
        "httpProxy":PROXY,
        "ftpProxy":PROXY,
        "sslProxy":PROXY,
        "noProxy":None,
        "proxyType":"MANUAL",
        "autodetect":False
    }
    driver = webdriver.Chrome()
    driver.get(dataset["webaddress"])
    time.sleep(4)
    path = dataset["gender"]+str(dataset["year"])+"/top_level_results/"+dataset["savepath"]
    unused = self.findMissing(path)
    for missingSheet in unused:
      pageNum = self.gotoPage(driver, missingSheet)
      time.sleep(5)
      content = driver.page_source
      df = self.pageExtract(content)
      df.to_json(path+"/resultsPgi"+pageNum+".json", orient='index')
      print('wrote missing sheet '+pageNum)

    i = 0
    b = 0
    time.sleep(5)
    while b < 1000:
      content = driver.page_source
      df = self.pageExtract(content)
      df.to_json(path+"/resultsPgi"+pageNum+".json", orient='index')
      print('wrote sheet '+pageNum)
      pageNum = self.nextPage(driver)
      time.sleep(2)
      
      i+=1
      if i > 100:
        time.sleep(15)
        i = 0
        b += 1
      pass
      # prefix = 'http://fantasy.espn.com/tournament-challenge-bracket/2019/en/'

class BracketScrape:
  def __init__(self):
    pass
  
  def pass_to_consolidated(self, PROXY, dataset):
    webdriver.DesiredCapabilities.CHROME['proxy']={
        "httpProxy":PROXY,
        "ftpProxy":PROXY,
        "sslProxy":PROXY,
        "noProxy":None,
        "proxyType":"MANUAL",
        "autodetect":False
    }
    # driver = webdriver.Chrome()
    # driver.get(dataset["webaddress"])
    path_open = dataset["gender"]+str(dataset["year"])+"/top_level_results/"+dataset["savepath"]+"/"
    # path_open = "scraped_brackets/"+str(dataset["year"])+"/top_level_results/test/"

    path_consolidated = dataset["gender"]+str(dataset["year"])+"/bracket_results/"+dataset["prefix"]+"_"
    open_file = open(path_consolidated+"consolidated.json", "a")
    c = {}
    for filename in os.listdir(path_open):
      with open(path_open+filename, "r") as read_file:
        data = json.load(read_file)
        for entry in data:
          # print(data[entry])
          entryID = data[entry]["Link"].split("=")[1]
          new_entry = dict({
            "team_picks" : {},
            "actual_results" : {
              "score" : data[entry]["Total"],
              "percentile" : data[entry]["Percentile"]
            },
          })
          c[entryID] = new_entry
          # json.dump(new_entry,open_file)
      # print("read file "+str(filename))
    json.dump(c, open_file)
    print("file ")

  def open_consolidated(self, PROXY, dataset):
    path_consolidated = dataset["gender"]+str(dataset["year"])+"/bracket_results/"+dataset["prefix"]+"_"
    open_file = open(path_consolidated+"consolidated.json", "r")
    d = json.load(open_file)
    open_file.close()
    empty_bracket = open(dataset["gender"]+str(dataset["year"])+"/empty.json", "r")
    reverse_lookup_file = open(dataset["gender"]+str(dataset["year"])+"/reverse_lookup.json", "r")
    eb = json.load(empty_bracket)
    reverse_bracket = json.load(reverse_lookup_file)

    webdriver.DesiredCapabilities.CHROME['proxy']={
        "httpProxy":PROXY,
        "ftpProxy":PROXY,
        "sslProxy":PROXY,
        "noProxy":None,
        "proxyType":"MANUAL",
        "autodetect":False
    }
    

    # driver = webdriver.Chrome()
    tp = []
    j = 0
    for key in d:
      if len(d[key]["team_picks"]) == 0:
        team_picks = json.loads(json.dumps(eb))
        page = requests.get("http://fantasy.espn.com/tournament-challenge-bracket/2019/en/entry?entryID="+key)
        # print(page.text)
        soup = BeautifulSoup(page.content, 'html.parser')
        c = soup.select(".selectedToAdvance")
        for i in c:
          # print(i)
          for child in i.contents:
            if "title" in child.attrs:
              team = child.attrs["title"]
              break
          region = reverse_bracket[team]["region"]
          seed = reverse_bracket[team]["seed"]
          # I have to add this one because this is the easiest way to fix issues with multiple demons being used for the same team i.e. VCU versus Virginia Commonwealth
          team = reverse_bracket[team]["team"]
          if(team_picks[region][seed][team] < 7):
            team_picks[region][seed][team] += 1
          # if team in team_picks.keys():
          #   if team_picks[team] < 7:
          #     team_picks[team] += 1
          # else:
          #   team_picks[team] = 2
        d[key]["team_picks"] = team_picks
        tp.append(team_picks)
        # print(c)
        # driver.get("http://fantasy.espn.com/tournament-challenge-bracket/2019/en/entry?entryID="+key)
        time.sleep(10)
        print(key+" added")
        j += 1
      else:
        print(key+ " already exists")
      if j == 10:
        j=0
        open_file = open(path_consolidated+"consolidated.json", "w")
        json.dump(d, open_file)
        print("finished saving!")
    pass





