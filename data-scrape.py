# from selenium import webdriver
# import pandas as pd
# import requests

from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
import pandas as pd
import time

# webdriver = "C:\Program Files (x86)\Google\Chrome\Application"
driver = Chrome()
products=[] #List to store name of the product
prices=[] #List to store price of the product
ratings=[] #List to store rating of the product
driver.get("http://fantasy.espn.com/tournament-challenge-bracket/2019/en/group?groupID=1041234")
time.sleep(4)

next_button = driver.find_element_by_css_selector('a.nextPage')
# next_button.click()
time.sleep(2)

content = driver.page_source
soup = BeautifulSoup(content, 'html.parser')
# time.sleep(4)
result = soup.select('div.mpTable')[0].select('tbody')[0] # main table
i = 1
# resultB = soup.select('div.mpTable')[0].select('tbody')[0]
time.sleep(2)

ranks=[] #Ranks
entries=[] #Ranks
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

  print(i, rank, name, bracketlink, r64, r32, r16, r8, r4, r2, champ, total, percentile)
  i+=1
# for tr in soup.findAll('tr',href=True, attrs={'class':'_31qSD5'}):
#   name=tr.find('div', attrs={'class':'period_0'})
#   # price=a.find('div', attrs={'class':'_1vC4OE _2rQ-NK'})
#   # rating=a.find('div', attrs={'class':'hGSR34 _2beYZw'})
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
#   # prices.append(price.text)
#   # ratings.append(rating.text)

df = pd.DataFrame({'Rank':ranks,'Names':names,'Link':links,'R64':r64s,'R32':r32s,'R16':r16s,'R8':r8s,'R4':r4s,'R2':r2s,'Champ Pick':champs,'Total':totals,'Percentile':percentiles}) 
df.to_csv('results.csv',mode='a', header=True, index=False, encoding='utf-8')

# pages = 10

# for page in range(1,pages):

#     url = "http://quotes.toscrape.com/js/page/" + str(page) + "/"

#     driver.get(url)

#     items = len(driver.find_elements_by_class_name("quote"))

#     total = []
#     for item in range(items):
#         quotes = driver.find_elements_by_class_name("quote")
#         for quote in quotes:
#             quote_text = quote.find_element_by_class_name('text').text
#             author = quote.find_element_by_class_name('author').text
#             new = ((quote_text,author))
#             total.append(new)
#     df = pd.DataFrame(total,columns=['quote','author'])
#     df.to_csv('quoted.csv')
# driver.close()


# URL = 'https://www.monster.com/jobs/search/?q=Software-Developer&where=Australia'
# page = requests.get(URL)

# soup = BeautifulSoup(page.content, 'html.parser')
# results = soup.find(id='ResultsContainer')

# job_elems = results.find_all('section', class_='card-content')

# for job_elem in job_elems:
#     # Each job_elem is a new BeautifulSoup object.
#     # You can use the same methods on it as you did before.
#     title_elem = job_elem.find('h2', class_='title')
#     company_elem = job_elem.find('div', class_='company')
#     location_elem = job_elem.find('div', class_='location')
#     print(title_elem)
#     print(company_elem)
#     print(location_elem)
#     print()

