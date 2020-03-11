from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import lxml.html as lh
import time
import requests
import os
import re

def csv_combine(forecast_path, who_picked_path):
  if os.path.exists(forecast_path):
    print("path exists")
  else:
    print(" path doesn't exist")
  forecast = pd.read_csv(forecast_path)
  who_picked = pd.read_csv(who_picked_path)
  
  print(forecast)
  print(who_picked)

forecast_path = "data/2019_men_who_picked.csv"
who_picked_path = "data/2019_fivethirtyeight_ncaa_forecasts.csv"
csv_combine(forecast_path, who_picked_path)