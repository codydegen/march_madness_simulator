import json
import sqlite3
import os
import requests
import random
from pathlib import Path
from bs4 import BeautifulSoup
import time

def populate_teams_table(db, teams):
  # Add teams table
  columns = ["name", "region", "seed", "elo", "pick_rate_1", "pick_rate_2", "pick_rate_3", "pick_rate_4", "pick_rate_5", "pick_rate_6", "pick_rate_7"]
  with db:
    current = db.cursor()
    i=1
    for region in teams:
      for seed in teams[region]:
        for team in teams[region][seed]:
          picked_frequency = [None] * 7
          for pick in team["picked_frequency"]:
            picked_frequency[int(pick)-1] = round(float(team["picked_frequency"][pick].strip("%"))*.01, 3)
          # print(team)
          data = [team["name"], region, int(seed), team["elo"]] + picked_frequency
          data = tuple(data)
          i += 1
          # print(data)
          query = '''INSERT OR IGNORE INTO teams ('''+", ".join(columns)+''') VALUES (?'''+",?"*(len(data)-1)+''')''' # WHERE NOT EXISTS (SELECT * FROM teams WHERE team = '''+team["name"]+''')'''

          current.execute(query, data)

def populate_entries_table(db, entries, group_id):
  print("populating entries table")
  with db:
    current = db.cursor()
    for entry in entries:
      add_entries_to_database(db, entry, entries)
      add_group_entries_to_database(db, group_id, entry)
    db.commit()

def add_entries_to_database(db, entry, entries):
  current = db.cursor()
  entry_query = '''INSERT OR IGNORE INTO entries (id, name, espn_score, espn_percentile) 
                                  VALUES (?,?,?,?);'''
  entry_data = (int(entry), "NULL", int(entries[entry]["actual_results"]["score"]), float(entries[entry]["actual_results"]["percentile"]))
  current.execute(entry_query, entry_data)
  return entry



def scrape_data_for_entries(db, ip_addresses):
  # take key from database
  current_path = os.path.dirname(__file__)
  empty_bracket_file = open(os.path.join(current_path, r"..\\web_scraper\\m2019\\empty.json"), "r")
  reverse_lookup_file = open(os.path.join(current_path, r"..\\web_scraper\\m2019\\reverse_lookup.json"), "r")
  reverse_bracket = json.load(reverse_lookup_file)
  empty_bracket = json.load(empty_bracket_file)

  # identify whether there are picks for this entry
  with db:
    current = db.cursor()
    select_table_query = ''' SELECT *  FROM entries 
                             WHERE name = 'NULL' AND entries.espn_score <> 0;'''
    current.execute(select_table_query)
    valid_keys = current.fetchall()
  # establish a proxy
  for key in valid_keys:
    url = "http://fantasy.espn.com/tournament-challenge-bracket/2019/en/entry?entryID="+str(key[0])
    try:
      proxy_index = random.randint(0, len(ip_addresses) - 1)
      proxies = {"http": ip_addresses[proxy_index], 
              "https": ip_addresses[proxy_index]}

      page = requests.get(url, proxies=proxies)
      soup = BeautifulSoup(page.content, 'html.parser')
      entry_id = key[0]
      user_picked_teams = soup.select(".selectedToAdvance")
      user_groups = soup.select(".user-entries-entry-groups")
      username = soup.select(".profileLink")
      entry_name = soup.select(".entry-details-entryname")
      predicted_score_winner = soup.select("#t1")
      predicted_score_loser = soup.select("#t2")
      if(len(predicted_score_winner) > 0):
        wins_array = get_wins_array(db, user_picked_teams, empty_bracket, reverse_bracket, entry_id)
        update_entry_with_entry_name_and_predicted_scores(db, key, entry_name, predicted_score_winner, predicted_score_loser, wins_array)
        user_id = add_user_to_database(db, username)
        user_entry_id = add_user_entries_to_database(db, user_id, key)
        add_other_user_brackets_to_database(db)
        add_groups_and_group_entries_to_database(db, user_groups, entry_id)
        db.commit()
        print("\n\ndata updated for entry "+str(entry_id))
      else:
        print("\n\nno bracket was filled out for entry "+str(entry_id))
        # time.sleep(3)
    except:
      ip_addresses.pop(proxy_index)
      print("proxy failed, remaining proxies: "+str(len(ip_addresses)))


def update_entry_with_entry_name_and_predicted_scores(db, entry, entry_html, predicted_score_winner_html, predicted_score_loser_html, wins_array):
  predicted_score_winner = int(predicted_score_winner_html[0].attrs['value'])
  predicted_score_loser = int(predicted_score_loser_html[0].attrs['value'])
  entry_id = entry[0]
  assert len(entry_html) == 1, " more than one entry name been identified"
  entry_name = entry_html[0].text
  current = db.cursor()
  team_array = []
  for i in range(1,69):
    team_array.append(", team_"+str(i)+"_wins = ?")
  query = '''UPDATE entries
              SET name = ?, predicted_score_winner = ?, predicted_score_loser = ? '''+"".join(team_array)+'''
              WHERE id = ?'''
  data = [entry_name, predicted_score_winner, predicted_score_loser] + wins_array + [entry_id]
  data = tuple(data)
  current.execute(query, data)
  confirm_query = '''SELECT * FROM entries
                      WHERE id = ?'''
  validation_data = tuple([entry_id])
  return entry_id

def add_user_to_database(db, username_html):
  # Add users into the database
  assert len(username_html) == 1, " more than one username name been identified"
  name = username_html[0].text
  current = db.cursor()
  query = '''INSERT OR IGNORE INTO users (name) 
                  VALUES (?);'''
  data = tuple([name])
  current.execute(query, data)
  last_id = current.lastrowid
  if last_id == 0:
    print(" user already in users table")
    validation_query = '''SELECT DISTINCT id FROM users
                            WHERE name = ?;'''
    validation = current.execute(validation_query, data).fetchone()[0]
    return validation
  else:
    print("new entry, username is "+name+", ID is "+str(last_id))
    return last_id 

def add_user_entries_to_database(db, user_id, entry):
  # Connect user IDs to entry IDs
  current = db.cursor()
  entry_id = entry[0]
  query = '''INSERT OR IGNORE INTO user_entries (id, user_id, entry_id)
                VALUES (?,?,?);'''
  new_id = "u"+str(user_id)+"e"+str(entry_id)
  data = (new_id, user_id, entry_id)
  current.execute(query, data)
  # db.commit()
  last_id = current.lastrowid
  if last_id == 0:
    print(" entry already in user_entries table")
    validation_query = '''SELECT id FROM user_entries
                            WHERE id = ?;'''
    
    validation = current.execute(validation_query, tuple([new_id]))
    return validation
  else:
    print("new user, ID is "+str(last_id))
    return last_id 

  

def add_other_user_brackets_to_database(db):
  # right now I'm not sure how to identify other entries from a single user.
  pass

def add_groups_and_group_entries_to_database(db, user_groups, entry_id):
  # This might be a place to eventually refactor code to be a little bit cleaner.
  # user_groups is the element that shows the list of groups. It can be in various forms ( single element, list of elements, drop-down menu)
  # And as such needs to be processed slightly differently.

  # Code block for if it's a drop-down menu
  if len(user_groups[0].contents) == 3:
    group_list = user_groups[0].contents[2]
    if "groupConsolidator" in group_list.attrs['class']:
      for option in group_list.contents[1].contents:
        # Some of the instances are empty strings, this removes that
        if not isinstance(option, str):
          if option.attrs["value"] != "":
            group_id = option.attrs["value"].split("=")[1]
            group_name = option.text.strip()
            add_group_to_database(db, group_id, group_name)
            add_group_entries_to_database(db, group_id, entry_id)
          pass
      pass
    else:
      for group in user_groups[0].contents:
        if group.name == "a":
          group_id = group.attrs["href"].split("=")[1]
          group_name = group.text.strip()
          add_group_to_database(db, group_id, group_name)
          add_group_entries_to_database(db, group_id, entry_id)
      # assert False, "add text"
  elif len(user_groups[0].contents) == 4:
    for group in user_groups[0].contents:
      if group.name == "a":
        group_id = group.attrs["href"].split("=")[1]
        group_name = group.text.strip()
        add_group_to_database(db, group_id, group_name)
        add_group_entries_to_database(db, group_id, entry_id)

  else:
    group = user_groups[0].contents[1]
    group_id = group.attrs["href"].split("=")[1]
    group_name = group.text.strip()
    add_group_to_database(db, group_id, group_name)
    add_group_entries_to_database(db, group_id, entry_id)



def add_group_to_database(db, group_id, group_name):
  current = db.cursor()
  data = (group_id, group_name)
  query = '''INSERT OR IGNORE INTO groups (id, name) VALUES (?,?);'''
  current.execute(query, data)
  db.commit()
  if current.lastrowid == group_id:
    print(" adding group "+str(group_name)+" with group ID "+str(group_id))
  return group_id

def add_group_entries_to_database(db, group_id, entry_id):
  current = db.cursor()
  group_entries_id = "g"+str(group_id)+"_e"+str(entry_id)
  group_entries_query = '''INSERT OR IGNORE INTO group_entries (id, entry_id, group_id) 
                              VALUES (?,?,?)'''
  group_entries_data = (group_entries_id, entry_id, group_id)
  current.execute(group_entries_query, group_entries_data)
  return group_entries_id

def get_wins_array(db, user_picked_teams, empty_bracket, reverse_bracket, entry_id):
  
  team_array = []
  for i in range(1,69):
    team_array.append("team_"+str(i)+"_wins")
  


  # team_picks = json.load(empty_bracket)
  team_picks = json.loads(json.dumps(empty_bracket))
  for game in user_picked_teams:
    # print(i)
    for child in game.contents:
      if "title" in child.attrs:
        team = child.attrs["title"]
        break
    region = reverse_bracket[team]["region"]
    seed = reverse_bracket[team]["seed"]
    # I have to add this one because this is the easiest way to fix issues with multiple names being used for the same team i.e. VCU versus Virginia Commonwealth
    team = reverse_bracket[team]["team"]
    if(team_picks[region][seed][team] < 7):
      team_picks[region][seed][team] += 1
  # print(team_picks)
  # can probably eventually do this faster
  current = db.cursor()
  team_query = '''SELECT * FROM teams;'''
  team_table = current.execute(team_query).fetchall()

  wins_array = []
  for team in team_table:
    # team_id = team[0]
    wins_array.append(team_picks[team[2]][str(team[3])][team[1]])
    # picks_query = '''INSERT OR IGNORE INTO picks (id, entry_id, team_id, wins) 
    #                       VALUES (?,?,?,?)'''
    # picks_data = (pick_id, entry_id, team_id, wins)
    # current.execute(picks_query, picks_data)
  return wins_array  


def migrate_entries_from_picks_to_entries(db):
  # Get all data from current entries table
  current = db.cursor()
  entries_query = '''SELECT * FROM entries'''
  entries_table = current.execute(entries_query).fetchall()
  
  team_array = []
  for i in range(1,69):
    team_array.append("team_"+str(i)+"_wins")

  # port it into entries migrated table
  for entry in entries_table:
    picks_query = '''SELECT * FROM  picks WHERE entry_id = ?'''
    picks_table = current.execute(picks_query, tuple([entry[0]])).fetchall()

    picks_data = [entry[0],entry[1],entry[2],entry[3],entry[4],entry[5]]
    for p in picks_table:
      picks_data.append(p[3])
    if len(picks_table) == 0:
      entry_query = '''INSERT OR IGNORE INTO entries_migrated (id, name, espn_score, espn_percentile, predicted_score_winner, predicted_score_loser)
                        VALUES (?'''+",?"*(len(picks_data)-1)+''')'''
    else:
      entry_query = '''INSERT OR IGNORE INTO entries_migrated (id, name, espn_score, espn_percentile, predicted_score_winner, predicted_score_loser,'''+", ".join(team_array)+''')
                          VALUES (?'''+",?"*(len(picks_data)-1)+''')'''
    entry_data = tuple(picks_data)
    current.execute(entry_query, entry_data)
    db.commit()
    print("commited entry ID "+str(entry[0]))
  
  # Iterate through pics table and add pics to entries
  pass

def main():
  team_data = r'..\\team_data\\team_m2019_20200407_0840.json'
  entries_data = r'..\\web_scraper\\m2019\\bracket_results\\sc_consolidated.json'
  

  current_path = os.path.dirname(__file__)
  new_team_data = os.path.join(current_path, team_data)
  new_entries_data = os.path.join(current_path, entries_data)

  teams = json.load(open(new_team_data, "r"))
  entries = json.load(open(new_entries_data, "r"))

  database_string = r"db\\m2019.db"
  db = sqlite3.connect(database_string)
  # migrate_entries_from_picks_to_entries(db)
  # populate_teams_table(db, teams)
  # add_group_to_database(db, 2895266, "Highly Questionable!")
  # populate_entries_table(db, entries, 1041234)
  # ip_addresses = ["52.179.231.206:80", 
                  # "52.179.231.206:80"]
  ip_addresses = ["52.179.231.206:80", 
                  "68.188.59.198:80",
                  "50.206.25.111:80",
                  "50.206.25.110:80",
                  "50.206.25.104:80",
                  "50.206.25.106:80",
                  "50.206.25.107:80",
                  "68.185.57.66:80",
                  "206.127.88.18:80",
                  "138.197.203.149:8080",
                  "138.68.43.159:8080",
                  "134.209.44.228:80",
                  "52.179.231.206:80",
                  "50.197.38.230:60724",
                  "108.177.235.174:3128",
                  "192.41.71.199:3128",
                  "206.223.238.72:22871",
                  "136.25.2.43:40017",
                  "144.34.195.56:80"
                  ]
  scrape_data_for_entries(db, ip_addresses)
  
if __name__ == '__main__':
    main()