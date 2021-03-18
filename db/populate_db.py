import json
import sqlite3
import os
import requests
import random
from pathlib import Path
from bs4 import BeautifulSoup
import time

import requests
import os, sys

if sys.version_info.major < 3:
    from urllib import url2pathname
else:
    from urllib.request import url2pathname

class LocalFileAdapter(requests.adapters.BaseAdapter):
    """Protocol Adapter to allow Requests to GET file:// URLs

    @todo: Properly handle non-empty hostname portions.
    """

    @staticmethod
    def _chkpath(method, path):
        """Return an HTTP status for the given filesystem path."""
        if method.lower() in ('put', 'delete'):
            return 501, "Not Implemented"  # TODO
        elif method.lower() not in ('get', 'head'):
            return 405, "Method Not Allowed"
        elif os.path.isdir(path):
            return 400, "Path Not A File"
        elif not os.path.isfile(path):
            return 404, "File Not Found"
        elif not os.access(path, os.R_OK):
            return 403, "Access Denied"
        else:
            return 200, "OK"

    def send(self, req, **kwargs):  # pylint: disable=unused-argument
        """Return the file specified by the given request

        @type req: C{PreparedRequest}
        @todo: Should I bother filling `response.headers` and processing
               If-Modified-Since and friends using `os.stat`?
        """
        path = os.path.normcase(os.path.normpath(url2pathname(req.path_url)))
        response = requests.Response()

        response.status_code, response.reason = self._chkpath(req.method, path)
        if response.status_code == 200 and req.method.lower() != 'head':
            try:
                response.raw = open(path, 'rb')
            except (OSError, IOError) as err:
                response.status_code = 500
                response.reason = str(err)

        if isinstance(req.url, bytes):
            response.url = req.url.decode('utf-8')
        else:
            response.url = req.url

        response.request = req
        response.connection = self

        return response

    def close(self):
        pass


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



def scrape_data_for_entries(db, ip_addresses, gender):
  # take key from database
  current_path = os.path.dirname(__file__)
  empty_bracket_file = open(os.path.join(current_path, r"..\\web_scraper\\mens2021\\empty.json"), "r")
  reverse_lookup_file = open(os.path.join(current_path, r"..\\web_scraper\\mens2021\\reverse_lookup.json"), "r")
  reverse_bracket = json.load(reverse_lookup_file)
  empty_bracket = json.load(empty_bracket_file)

  # identify whether there are picks for this entry
  with db:
    current = db.cursor()
    select_table_query = ''' SELECT *  FROM entries 
                             WHERE name = 'NULL' AND entries.espn_score = 0;'''
    current.execute(select_table_query)
    valid_keys = current.fetchall()
  # establish a proxy
  for key in valid_keys:
    # url = "https://fantasy.espn.com/tournament-challenge-bracket/2021/en/entry?entryID="+str(key[0])
    url = "file:///C:/Users/Cody/Documents/Repo/march_madness_simulator/tc"+str(key[0])+".html"
    requests_session = requests.session()
    requests_session.mount('file://', LocalFileAdapter())
    page = requests_session.get('file:///C:/Users/Cody/Documents/Repo/march_madness_simulator/htmlbrackets/tc'+str(key[0])+'.html')
    if page.status_code != 404:
      proxy_index = random.randint(0, len(ip_addresses) - 1)
      proxies = {"http": ip_addresses[proxy_index], 
              "https": ip_addresses[proxy_index]}

      # page = requests.get(url)
      
      page = requests_session.get('file:///C:/Users/Cody/Documents/Repo/march_madness_simulator/htmlbrackets/tc'+str(key[0])+'.html')

      # page = requests.get(url, proxies=proxies)

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
        update_entry_with_entry_name_and_predicted_scores(db, key, entry_name, predicted_score_winner, predicted_score_loser, wins_array, gender)
        user_id = add_user_to_database(db, username)
        user_entry_id = add_user_entries_to_database(db, user_id, key)
        # add_other_user_brackets_to_database(db)
        # add_groups_and_group_entries_to_database(db, user_groups, entry_id)
        db.commit()
        print("\n\ndata updated for entry "+str(entry_id))
      else:
        print("\n\nno bracket was filled out for entry "+str(entry_id))
        # time.sleep(3)
    # except:
    #   ip_addresses.pop(proxy_index)
    #   print("proxy failed, remaining proxies: "+str(len(ip_addresses)))


def update_entry_with_entry_name_and_predicted_scores(db, entry, entry_html, predicted_score_winner_html, predicted_score_loser_html, wins_array, gender):
  predicted_score_winner = int(predicted_score_winner_html[0].attrs['value'])
  predicted_score_loser = int(predicted_score_loser_html[0].attrs['value'])
  entry_id = entry[0]
  assert len(entry_html) == 1, " more than one entry name been identified"
  entry_name = entry_html[0].text
  current = db.cursor()
  team_array = []
  if gender == "mens":
    num_teams = 68
  else:
    num_teams = 64
  for i in range(1,num_teams+1):
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
    # error here means you have to add an entry to the reverse lookup with the missing team names
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
  return wins_array  


def main(gender):
  team_data = r'..\\web_scraper\\mens2021\\preliminary_results.json'
  entries_data = r'..\\web_scraper\\mens2021\\bracket_results\\cd_consolidated.json'
  

  current_path = os.path.dirname(__file__)
  new_team_data = os.path.join(current_path, team_data)
  new_entries_data = os.path.join(current_path, entries_data)

  teams = json.load(open(new_team_data, "r"))
  entries = json.load(open(new_entries_data, "r"))

  database_string = r"db\\mens2021.db"
  db = sqlite3.connect(database_string)

  # Add only if teams haven't been added
  # populate_teams_table(db, teams)
  # Add only if groups haven't been added
  # add_group_to_database(db, 4144911, "just me")
  populate_entries_table(db, entries, 4144911)

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

  ip_addresses = ["52.179.231.206:80", 
                  "52.179.231.206:80"]
  scrape_data_for_entries(db, ip_addresses, gender)
  
if __name__ == '__main__':
    main("mens")



