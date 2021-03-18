from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import lxml.html as lh
import time
import requests
import os
import re



def csv_combine(year):
  forecast_path = str(year)+"_fivethirtyeight_ncaa_forecasts.csv"
  who_picked_path_men = str(year)+"_mens_who_picked.csv"
  who_picked_path_women = str(year)+"_womens_who_picked.csv"
  current_path = os.path.dirname(__file__)
  forecast_file = os.path.join(current_path, forecast_path)
  wpm = os.path.join(current_path, who_picked_path_men)
  wpw = os.path.join(current_path, who_picked_path_women)
  if os.path.exists(forecast_file):
    pass
  else:
    pass
    # print(" path doesn't exist")
  forecast = pd.read_csv(forecast_file)
  who_picked_men = pd.read_csv(wpm)
  who_picked_women = pd.read_csv(wpw)
  j = 0
  r64 = []
  r32 = []
  r16 = []
  r8 = []
  r4 = []
  r2 = []
  for i in range(0, len(forecast)):
    team_name = forecast.iloc[i]['team_name']
    if forecast.iloc[i]["gender"] == "mens":
      if team_name not in who_picked_men["team_name"].values:
        # print(team_name)
        # print(" incorrectly imported data")
        team_name = name_fix(team_name,"mens",year)
      
      subset = who_picked_men.loc[who_picked_men["team_name"] == team_name]
    elif forecast.iloc[i]["gender"] == "womens":
      if team_name not in who_picked_women["team_name"].values:
        # print(team_name)
        # print(" incorrectly imported data")
        team_name = name_fix(team_name,"womens",year)
      subset = who_picked_women.loc[who_picked_women["team_name"] == team_name]
    else:
      print("no gender")
    if subset.size==0:
      equivalent_seed = forecast.iloc[i]["team_seed"]
      region = forecast.iloc[i]["team_region"]
      if equivalent_seed[-1] == "b":
        new_seed = equivalent_seed[0:2]+"a"
        
      elif equivalent_seed[-1] == "a":
        new_seed = equivalent_seed[0:2]+"b"
      else:
        print(" missing seed")
      
      if forecast.iloc[i]["gender"] == "mens":
        # err here means missing name
        new_name = name_fix(forecast[(forecast["team_seed"] == new_seed) & (forecast["team_region"] == region) & (forecast["gender"] == "mens")]["team_name"].values[0],"men",year)
        subset = who_picked_men.loc[who_picked_men["team_name"] == new_name]
      elif forecast.iloc[i]["gender"] == "womens":
        new_name = name_fix(forecast[(forecast["team_seed"] == new_seed) & (forecast["team_region"] == region) & (forecast["gender"] == "womens")].values[0],"womens",year)
        subset = who_picked_women.loc[who_picked_women["team_name"] == new_name]
      j+=1
      # print("couldn't find "+team_name+" seed:"+equivalent_seed+". Replaced with "+new_name+", seed:"+new_seed+" "+str(j))
      r64.append(subset["R64"].values[0])
      r32.append(subset["R32"].values[0])
      r16.append(subset["S16"].values[0])
      r8.append(subset["E8"].values[0])
      r4.append(subset["F4"].values[0])
      r2.append(subset["NCG"].values[0])
      # pass
    else:
      r64.append(subset["R64"].values[0])
      r32.append(subset["R32"].values[0])
      r16.append(subset["S16"].values[0])
      r8.append(subset["E8"].values[0])
      r4.append(subset["F4"].values[0])
      r2.append(subset["NCG"].values[0])
  print("done")
  forecast['R64_picked'] = r64
  forecast['R32_picked'] = r32
  forecast['S16_picked'] = r16
  forecast['E8_picked'] = r8
  forecast['F4_picked'] = r4
  forecast['NCG_picked'] = r2
  output_path = os.path.join(current_path, str(year)+"_all_prepped_data.csv")
  with open(output_path, "w") as file:
    forecast.to_csv(file, index=False, line_terminator='\n')
    # print(subset)

    # print forecast.iloc[i]['team_name'], forecast.iloc[i]['team_seed']


  # for row in forecast.iterrows():
    
  #   print(row["team_name"], row["team_seed"])
  
  # print(forecast)
  # print(who_picked)


def name_fix(name, gender, year):
  swapper = {
    #538 : who picked
    # "North Carolina A&T": "NC A&T",
    "Appalachian State": "APP",
    "Eastern Washington": "E Washington",
    "UC-Santa Barbara": "UCSB",
    "Michigan State": "MSU",
    "Middle Tennessee": "Middle Tenn",
    "Louisiana State": "LSU",
    "Florida State": "Florida St",
    "Central Florida": "UCF",
    "UC-Irvine": "UC Irvine",
    "Virginia Commonwealth": "VCU",
    "Virginia": "UVA",
    "Mississippi State": "Mississippi St",
    "North Dakota State": "North Dakota St",
    "Fairleigh Dickinson": "F. Dickinson",
    "Northern Kentucky": "N Kentucky",
    "New Mexico State": "New Mexico St",
    "Abilene Christian": "Abil Christian",
    "Gardner-Webb": "GardnerWebb",
    "Mississippi": "Ole Miss",
    "Saint Mary's (CA)": "Saint Mary's",
    "North Carolina Central": "Saint Mary's",
    "Connecticut": "UConn",
    "North Carolina State": "NC State",
    "South Dakota State": "SDST",
    "Miami (FL)": "Miami",
    "Brigham Young": "BYU",
    "South Dakota": "SDAK",
    "Florida Gulf Coast": "FGCU",
    "Arkansas-Little Rock": "Little Rock",
    "Bethune-Cookman": "BethuneCookman",
    "Central Michigan": "CMU",
    "Cent Michigan": "CMU",
    "UC-Davis": "UC Davis",
    "Loyola (IL)": "LoyolaChicago",
    "Texas A&M": "Texas A&M;",
    "Maryland-Baltimore County": "UMBC",
    "Ohio State": "OSU",
    "North Carolina": "UNC",
    "Rhode Island": "URI",
    "North Carolina-Greensboro": "UNCG",
    "Pennsylvania": "Penn",
    "College of Charleston": "Charleston",
    "Texas Christian": "TCU",
    "Cal State Fullerton": "CSU Fullerton",
    "Stephen F. Austin": "SF Austin",
    "Saint Francis (PA)": "St Francis (PA)",
    "South Florida": "USF",
    "California": "Cal",
    "North Carolina A&T": "NC A&T",
    "Cal State Northridge": "CSU Northridge",
    "George Washington": "G Washington",
    "Western Kentucky": "W Kentucky",
    "Northern Colorado": "N Colorado",
    "Nicholls State": "Nicholls",
    "Southern California": "USC",
    "Norfolk State": "NORF",
    "Texas Southern": "TXSO",
    "Mount St. Mary's": "MSM",
    # "Mt. St. Mary's": "MSM",
    "Drake": "DRKE",
    "Washington State": "Washington St",
    # "LoyolaChicago": "Loyola Chicago",
    
    # "Mississippi State": ,
  }
  if name in swapper:
    if name == "Mount St. Mary's":
      if gender == "womens":
        return "Mt. St. Mary's"
      else:
        return "MSM"
    # if name == "Central Michigan":
    #   if year == 2021:
    #     return "Cent Michigan"
    #   else:
    #     return "CMU"
    if name == "North Carolina-Greensboro":
      if year == 2021:
        return "UNC Greensboro"
      else:
        return "UNCG"
    if name == "Loyola (IL)":
      if year == 2021:
        return "Loyola Chicago"
      else:
        return "LoyolaChicago"
    if name == "Mississippi State": 
      if gender == "mens":
        return "Mississippi St"
      else:
        if year == 2018:
          return "Miss St"
        else:
          return "MSST"
    if name == "Abilene Christian": 
      if gender == "mens":
        return "Abil Christian"
      else:
        return "ACU"
    if name == "New Mexico State": 
      if gender == "mens":
        return "New Mexico St"
      else:
        return "NMSU"
    if name == "Central Michigan":
      if year == 2018 or year == 2021:
        return "Cent Michigan"
      else:
        return "CMU"
    if name == "Florida State":
      if year == 2018:
        return "FSU"
      else:
        return "Florida St"
    if name == "South Dakota State":
      if year == 2018 or year == 2021:
        return "South Dakota St"
      else:
        return "SDST"
    return swapper[name]
  else:
    return name

csv_combine(2021)