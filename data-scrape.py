# from selenium import webdriver
# import pandas as pd
# import requests

from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
import pandas as pd
import time

def pageExtract(content):
  soup = BeautifulSoup(content, 'html.parser')
  result = soup.select('div.mpTable')[0].select('tbody')[0] # main table
  i = 1
  time.sleep(2)
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

def nextPage(driver):
  next_button = driver.find_element_by_css_selector('a.nextPage')
  next_button.click()
  time.sleep(1)
  pageNum = driver.find_element_by_css_selector('strong.selected')
  return str(pageNum.text)

def gotoPage(driver, pn):
  test_button_list = driver.find_element_by_css_selector('a.navigationLink.pageNumber')
  try:
    tb = driver.find_element_by_xpath("//a[@data-start='"+str((pn-1)*50)+"']")
    
  except:
    # finish this
    print("oops")
    tblist = driver.find_elements_by_css_selector("a.navigationLink.pageNumber")
    tblist[-1].click()
    print("oops")
  
  tb.click()
  time.sleep(1)
  return str(tb.text)

driver = Chrome()
driver.get("http://fantasy.espn.com/tournament-challenge-bracket/2019/en/group?groupID=1041234")
time.sleep(4)
# next_button = driver.find_element_by_css_selector('a.nextPage')
# pageNum = driver.find_element_by_css_selector('strong.selected')
pageNum = str(1)
content = driver.page_source
gotoPage(driver, 30)
df = pageExtract(content)
df.to_json('ESPN_sportscenter_2019/resultsPgi'+pageNum+'.json', orient='index')
pageNum = nextPage(driver)
content = driver.page_source
df = pageExtract(content)
df.to_json('resultsPg'+pageNum+'.json', orient='index')

prefix = 'http://fantasy.espn.com/tournament-challenge-bracket/2019/en/'






