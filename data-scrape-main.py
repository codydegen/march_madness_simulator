# from bs4 import BeautifulSoup
# from selenium import webdriver
# import pandas as pd
# import time
# import requests
import ds

# http://free-proxy.cz/en/proxylist/country/US/http/ping/all
PROXY = "156.96.118.58:3128"
PROXY = "52.179.231.206:80"

tournamentChallenge = {
  "groupname": "Tournament Challenge",
  "savepath": "Tournament_challenge_2019",
  "webaddress": "http://fantasy.espn.com/tournament-challenge-bracket/2019/en/group?groupID=196060",
  "groupsize": "100,000+"
}

sportsCenter = {
  "groupname": "ESPN's SportsCenter",
  "savepath": "ESPN_sportscenter_2019",
  "webaddress": "http://fantasy.espn.com/tournament-challenge-bracket/2019/en/group?groupID=1041234",
  "groupsize": "1,000,000+"
}



ds.main(PROXY, tournamentChallenge)
