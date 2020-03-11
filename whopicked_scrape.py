from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import lxml.html as lh
import time
import requests
import os

url='http://fantasy.espn.com/tournament-challenge-bracket/2019/en/whopickedwhom'
#Create a handle, page, to handle the contents of the website
page = requests.get(url)
#Store the contents of the website under doc
doc = lh.fromstring(page.content)
#Parse data that are stored between <tr>..</tr> of HTML
tr_elements = doc.xpath('//tr')
print([len(T) for T in tr_elements[:12]])

tr_elements = doc.xpath('//tr')
#Create empty list
col=[]
i=0
#For each row, store each first element (header) and an empty list
for t in tr_elements[0]:
    i+=1
    name=t.text_content()
    print '%d:"%s"'%(i,name)
    col.append((name,[]))

for j in range(1,len(tr_elements)):
    #T is our j'th row
    T=tr_elements[j]
    
    #If row is not of size 6, the //tr data is not from our table 
    if len(T)!=6:
        break
    
    #i is the index of our column
    i=0
    
    #Iterate through each element of the row
    for t in T.iterchildren():
        data=t.text_content() 
        #Check if row is empty
        if i>0:
        #Convert any numerical value to integers
            try:
                data=int(data)
            except:
                pass
        #Append the data to the empty list of the i'th column
        col[i][1].append(data)
        #Increment i for the next column
        i+=1
[len(C) for (title,C) in col]
Dict={title:column for (title,column) in col}
df=pd.DataFrame(Dict)
df.head()

# def findMissing(path):
#   i = 1
#   unused = []
#   discontinuity = False
#   while discontinuity == False:
#     if os.path.exists(path+"/resultsPgi"+str(i)+".json") == False:
#       unused.append(i)
#       print("missing sheet found: ", i)
#       if i-1 in unused:
#         discontinuity = True
#     i+=1
#   return unused

# def pageExtract(content):
#   soup = BeautifulSoup(content, 'html.parser')
#   result = soup.select('div.mpTable')[0].select('tbody')[0] # main table
#   i = 1
#   time.sleep(2)
#   ranks=[] #Rank
#   # entries=[] #Ranks
#   names=[] #Ranks
#   links=[] #Ranks
#   r64s=[] #Ranks
#   r32s=[] #Ranks
#   r16s=[] #Ranks
#   r8s=[] #Ranks
#   r4s=[] #Ranks
#   r2s=[] #Ranks
#   champs=[] #List to store price of the product
#   totals=[] #List to store rating of the product
#   percentiles=[] #List to store rating of the product
#   for tr in result.findAll('tr'):
#     rank = tr.find('td', attrs={'class':'rank'}).text
#     entry = tr.find('a', attrs={'class':'entry'})
#     name = entry.text
#     bracketlink = entry.attrs['href']
#     r64 = tr.find('td', attrs={'class':'period_0'}).text
#     r32 = tr.find('td', attrs={'class':'period_1'}).text
#     r16 = tr.find('td', attrs={'class':'period_2'}).text
#     r8 = tr.find('td', attrs={'class':'period_3'}).text
#     r4 = tr.find('td', attrs={'class':'period_4'}).text
#     r2 = tr.find('td', attrs={'class':'period_5'}).text
#     champ = tr.find('td', attrs={'class':'champ'}).text
#     total = tr.find('td', attrs={'class':'total'}).text
#     percentile = tr.find('td', attrs={'class':'percentile'}).text
#     i+=1
#     ranks.append(rank)
#     names.append(name)
#     links.append(bracketlink)
#     r64s.append(r64)
#     r32s.append(r32)
#     r16s.append(r16)
#     r8s.append(r8)
#     r4s.append(r4)
#     r2s.append(r2)
#     champs.append(champ)
#     totals.append(total)
#     percentiles.append(percentile)
#   data = {'Rank':ranks,'Names':names,'Link':links,'R64':r64s,'R32':r32s,'R16':r16s,'R8':r8s,'R4':r4s,'R2':r2s,'Champ Pick':champs,'Total':totals,'Percentile':percentiles}
#   df = pd.DataFrame(data, columns= ['Rank','Names','Link','R64','R32','R16','R8','R4','R2','Champ Pick','Total','Percentile']) 
#   return df

# def nextPage(driver):
#   next_button = driver.find_element_by_css_selector('a.nextPage')
#   next_button.click()
#   time.sleep(2)
#   pageNum = driver.find_element_by_css_selector('strong.selected')
#   return str(pageNum.text)

# def gotoPage(driver, pn):
#   try:
#     tb = driver.find_element_by_xpath("//a[@data-start='"+str((pn-1)*50)+"']")
#   except:
#     # finish this
#     print("oops")
#     found = False
#     while found == False:
#       tblist = driver.find_elements_by_css_selector("a.navigationLink.pageNumber")
#       try:
#         maxPage = int(tblist[-1].text)
#       except IndexError as err:
#         print('Index error, waiting: ', err)
#         time.sleep(5)
#         tblist = driver.find_elements_by_css_selector("a.navigationLink.pageNumber")
#         maxPage = int(tblist[-1].text)
#         pass
#       minPage = int(tblist[0].text)
#       if pn > maxPage:
#         tblist[-1].click()
#         time.sleep(3)
#       elif pn < minPage:
#         tblist[0].click()
#         time.sleep(3)
#       else:
#         for i in tblist:
#           if pn == int(i.text):
#             tb = i
#             found = True
#   tbpn = tb.text
#   tb.click()
#   time.sleep(1)
#   return str(tbpn)

# def main(PROXY, dataset):
#   webdriver.DesiredCapabilities.CHROME['proxy']={
#       "httpProxy":PROXY,
#       "ftpProxy":PROXY,
#       "sslProxy":PROXY,
#       "noProxy":None,
#       "proxyType":"MANUAL",
#       "autodetect":False
#   }
#   driver = webdriver.Chrome()
#   driver.get(dataset["webaddress"]) #Tournament Challenge 100k
#   time.sleep(4)
#   unused = findMissing(dataset["savepath"])
#   for missingSheet in unused:
#     pageNum = gotoPage(driver, missingSheet)
#     time.sleep(5)
#     content = driver.page_source
#     df = pageExtract(content)
#     df.to_json(dataset["savepath"]+"/resultsPgi"+pageNum+".json", orient='index')
#     print('wrote missing sheet '+pageNum)

#   i = 0
#   b = 0
#   time.sleep(5)
#   while b < 1000:
#     content = driver.page_source
#     df = pageExtract(content)
#     df.to_json(dataset["savepath"]+"/resultsPgi"+pageNum+".json", orient='index')
#     print('wrote sheet '+pageNum)
#     pageNum = nextPage(driver)
#     time.sleep(2)
    
#     i+=1
#     if i > 100:
#       time.sleep(15)
#       i = 0
#       b += 1
#     pass


# # prefix = 'http://fantasy.espn.com/tournament-challenge-bracket/2019/en/'