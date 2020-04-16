#! python3
import random
import math
import pandas as pd
from pandas import DataFrame as df
from anytree import Node, RenderTree, NodeMixin, AsciiStyle
from anytree.exporter import DotExporter, JsonExporter
from anytree.importer import JsonImporter
import os
import copy
import time
import json
import queue
import csv
import sqlite3
import statistics
import matplotlib.pyplot as plt


final_four_pairings = {
  "mens" : {
    2019 : 
      [['East', 'West'], 
      ['Midwest', 'South']]
    ,
    2018 : {
      # TBD
    }
  },
  "womens" : {
    2019 : {
      # tbd
    },
    2018 : {
      # TBD
    }
  }
}

# different scoring systems for different brackets so expected points can be 
# calculated
scoring_systems = {
  "ESPN" : {
    "round" : {
      0 : 0,
      1 : 0,
      2 : 10,
      3 : 20,
      4 : 40,
      5 : 80,
      6 : 160,
      7 : 320,
      },
    "cumulative" : {
      0 : 0,
      1 : 0,
      2 : 10,
      3 : 30,
      4 : 70,
      5 : 150,
      6 : 310,
      7 : 630,
      },
  },

  "wins_only" : {
    "round" : {
      0 : 0,
      1 : 0,
      2 : 1,
      3 : 1,
      4 : 1,
      5 : 1,
      6 : 1,
      7 : 1,
    }, 
    "cumulative" : {
      0 : 0,
      1 : 0,
      2 : 1,
      3 : 2,
      4 : 3,
      5 : 4,
      6 : 5,
      7 : 6,
      },
  },

  "degen_bracket" : {
    "round" : {
      0 : 0,
      1 : 0,
      2 : 2,
      3 : 3,
      4 : 5,
      5 : 8,
      6 : 13,
      7 : 21,
    },
    "cumulative" : {
      0 : 0,
      1 : 0,
      2 : 2,
      3 : 5,
      4 : 10,
      5 : 18,
      6 : 31,
      7 : 52,
      },
  }
}


# seed pairings used to build the initial bracket
seed_pairings = [[1,16],
                 [8,9],
                 [5,12],
                 [4,13],
                 [6,11],
                 [3,14],
                 [7,10],
                 [2,15]]

class Model:
  def __init__(self, gender='mens', year=2019, number_simulations=1, scoring_system=scoring_systems["ESPN"]):
    self.gender = gender
    self.year = year 
    self.all_teams = self.create_teams()
    self.start_bracket = Bracket(model=self)
    self.sim_bracket = Bracket(model=self)
    self.game_pairing = 0
    self.number_simulations = number_simulations
    self.completed_simulations = 0
    self.scoring_system = scoring_system

    self.actual_results = None
    self.simulation_results = []
    self.special_entries = {
      "most_valuable_teams": None,
      "most_popular_teams": None,
      "chalk": None,
    }
    self.simulations_won_by_special_entries = {
      "most_valuable_teams": 0,
      "most_popular_teams": 0,
      "chalk": 0,
    }
    self.entries = {
      "imported_entries": [],
      # "actual_results": None,
      "most_valuable_teams": None,
      "most_popular_teams": None,
      "chalk": None,
    }
    self.simulations_won_by_imported_entries = []
    self.winning_scores_of_simulations = []
    pass

  def create_teams(self):
    # Not sure why this starts for the root directory and not the location of 
    # the file.  I would've thought that moving model.py would've necessitated 
    # changing this path but it didn't.
    current_path = os.path.dirname(__file__)
    team_data = "../team_data/"+str(self.year)+"_all_prepped_data.csv"
    path = os.path.join(current_path, team_data)

    
    all_teams = {}
    if os.path.exists(path):
      print(" found data")
      
    else:
      print(" couldn't find data")
      # TBD, hook up data scraping to this
      raise Exception("There is no data for this combination of team and year")
      # a = self.prep_data(path)

    team_data = pd.read_csv(path)
    gender_specific = team_data[team_data.gender == self.gender]
    earliest_date = gender_specific.forecast_date[-1:].values[-1]
    # data subset is the teams from the earliest date shown. This is the data 
    # from all of the teams are still in the tournament
    df = gender_specific[gender_specific.forecast_date == earliest_date]
    for ind in df.index:
      picks = {
        1:'100.0%',
        2:df["R64_picked"][ind], 
        3:df["R32_picked"][ind], 
        4:df["S16_picked"][ind], 
        5:df["E8_picked"][ind], 
        6:df["F4_picked"][ind], 
        7:df["NCG_picked"][ind], 
      }
      team_name = df["team_name"][ind]
      team_seed = df["team_seed"][ind]
      # team seeds in the imported file have an a or B suffix for playin games, 
      # this strips that 
      if len(team_seed) > 2:
        team_seed = team_seed[0:2]
      team_region = df["team_region"][ind]
      team_rating = df["team_rating"][ind]
      team = Team(team_name, team_seed, team_region, team_rating, picks)
      if team_region not in all_teams:
        all_teams[team_region] = {}
      if team_seed not in all_teams[team_region]:
        all_teams[team_region][team_seed] = [team]
      else:
        all_teams[team_region][team_seed].append(team)
    return all_teams
    
  def team_look_up(self, team):
    teams = self.all_teams[team.region][team.seed]
    if len(teams) == 1:
      return teams[0]
    else:
      if teams[0].name == team.name:
        return teams[0]
      elif teams[1].name == team.name:
        return teams[1]
      else:
        assert False, "couldn't find team"

  def reset_bracket(self):
    self.sim_bracket.reset_bracket()
    pass

# simulation methods
  def batch_simulate(self):
    for i in range(0, self.number_simulations):
      # t = time.time()
      self.sim_bracket.simulate_bracket()
      self.update_scores()
      self.reset_bracket()
      self.completed_simulations += 1
      # if self.completed_simulations%100 == 0:
      # print("simulation number "+str(i)+" completed.")
    self.calculate_expected_points()

  def update_scores(self):
    for region in self.all_teams:
      for seed in self.all_teams[region]:
        for team in self.all_teams[region][seed]:
          team.simulation_results.append(team.temp_result)
          if team.simulation_results[-1] == 0 and len(self.all_teams[region][seed]) == 1:
            team.simulation_results[-1] = 1
          team.temp_result = 0
          pass

  
  def calculate_expected_points(self):
    for region in self.all_teams:
      for seed in self.all_teams[region]:
        for team in self.all_teams[region][seed]:
          total_expected_points = 0
          for ep in team.expected_points:
            round_expected_points = float(team.wins[ep]) / float(self.number_simulations) * float(self.scoring_system["round"][ep])
            team.expected_points[ep] = round_expected_points
            total_expected_points += round_expected_points
          team.total_expected_points = total_expected_points
          print(team.name+" expected points: "+str(team.total_expected_points))
    pass

  def output_most_valuable_bracket(self):
    # (TD) this can be exported into JSON format without going into the intermediate bracket step
    self.calculate_expected_points()
    most_valuable_bracket = Bracket(self)
    self.postprocess_bracket(most_valuable_bracket, "expected_points")
    return most_valuable_bracket

  def output_most_popular_bracket(self):
    # (TD) this can be exported into JSON format without going into the intermediate bracket step
    # self.calculate_expected_points()
    most_popular_bracket = Bracket(self)
    self.postprocess_bracket(most_popular_bracket, "picked_frequency")
    return most_popular_bracket

  def update_entry_picks(self):
    team_data = r'..\\web_scraper\\'+model.gender+str(model.year)+r'\\actual.json'
    # chalk_data = r'..\\web_scraper\\'+model.gender+str(model.year)+r'\\chalk.json'
    current_path = os.path.dirname(__file__)
    new_team_data = os.path.join(current_path, team_data)
    # chalk_team_data = os.path.join(current_path, chalk_data)
    actual_results = json.load(open(new_team_data, "r"))
    # chalk_results = json.load(open(chalk_team_data, "r"))

    for region in actual_results:
      for seed in actual_results[region]:
        for team in actual_results[region][seed]:
          if self.all_teams[region][seed][0].name == team:
            self.all_teams[region][seed][0].entry_picks["actual_results"] = actual_results[region][seed][team]
            # self.all_teams[region][seed][0].entry_picks["chalk"] = chalk_results[region][seed][team]
            # self.all_teams[region][seed][0].entry_picks["most_valuable_teams"] = self.entries["most_valuable_teams"].team_picks[region][seed][team]
            # self.all_teams[region][seed][0].entry_picks["most_popular_teams"] = self.entries["most_popular_teams"].team_picks[region][seed][team]
          else:
            self.all_teams[region][seed][1].entry_picks["actual_results"] = actual_results[region][seed][team]
            # self.all_teams[region][seed][1].entry_picks["chalk"] = chalk_results[region][seed][team]
            # self.all_teams[region][seed][1].entry_picks["most_valuable_teams"] = self.entries["most_valuable_teams"].team_picks[region][seed][team]
            # self.all_teams[region][seed][1].entry_picks["most_popular_teams"] = self.entries["most_popular_teams"].team_picks[region][seed][team]
    # actual_results = Bracket(self)
    # self.update_entry_picks(actual_results)
    entry = {
      "team_picks" : actual_results,
      "name" : "Actual results",
      "entryID" : -1,
      "method" : "Actual results",
      "source" : "Actual results"
    }

    # chalk_entry = {
    #   "team_picks" : chalk_results,
    #   "name" : "Chalk entry",
    #   "entryID" : -1,
    #   "method" : "Chalk entry",
    #   "source" : "Chalk entry"
    # }

    self.entries["actual_results"] = Entry(source=json.dumps(entry), method="json")
    # self.entries["chalk"] = Entry(source=json.dumps(chalk_entry), method="json")
    # return actual_results

  def initialize_special_entries(self):
    # Initialize the special entries including:
    # Most valuable bracket, most popular bracket, chalk bracket
    most_valuable_bracket = self.output_most_valuable_bracket()
    most_popular_bracket = self.output_most_popular_bracket()
    current_path = os.path.dirname(__file__)
    chalk_data = r'..\\web_scraper\\'+model.gender+str(model.year)+r'\\chalk.json'
    chalk_team_data = os.path.join(current_path, chalk_data)
    chalk_results = json.load(open(chalk_team_data, "r"))
    chalk_entry = {
      "team_picks" : chalk_results,
      "name" : "Chalk entry",
      "entryID" : -1,
      "method" : "Chalk entry",
      "source" : "Chalk entry"
    }
    mvb_source = model.sim_bracket.export_bracket_to_json(most_valuable_bracket.bracket.root, "most valuable bracket")
    mpb_source = model.sim_bracket.export_bracket_to_json(most_popular_bracket.bracket.root, "most popular bracket")
    self.special_entries["most_valuable_teams"] = Entry(source=mvb_source, method="json")
    self.special_entries["most_popular_teams"] = Entry(source=mpb_source, method="json")
    self.special_entries["chalk"] = Entry(source=json.dumps(chalk_entry), method="json")

  def analyze_special_entries(self):
    # Add in the results for special brackets including:
    # Most valuable bracket, most popular bracket, chalk bracket
    for entry in self.special_entries:
      self.update_special_entry_score(self.special_entries[entry], entry)
    # most_valuable_bracket = self.output_most_valuable_bracket()
    # most_popular_bracket = self.output_most_popular_bracket()
    # mvb_source = model.sim_bracket.export_bracket_to_json(most_valuable_bracket.bracket.root, "most valuable bracket")
    # mpb_source = model.sim_bracket.export_bracket_to_json(most_popular_bracket.bracket.root, "most popular bracket")
    # self.entries["most_valuable_teams"] = Entry(source=mvb_source, method="json")
    # self.entries["most_popular_teams"] = Entry(source=mpb_source, method="json")

    # self.update_entry_picks()


  def postprocess_via_popularity_and_value(self):
    # Add most valuable and most picked brackets
    most_valuable_bracket = self.output_most_valuable_bracket()
    most_popular_bracket = self.output_most_popular_bracket()
    mvb_source = model.sim_bracket.export_bracket_to_json(most_valuable_bracket.bracket.root, "most valuable bracket")
    mpb_source = model.sim_bracket.export_bracket_to_json(most_popular_bracket.bracket.root, "most popular bracket")
    self.entries["most_valuable_teams"] = Entry(source=mvb_source, method="json")
    self.update_special_entry_score(self.entries["most_valuable_teams"])
    self.entries["most_popular_teams"] = Entry(source=mpb_source, method="json")
    
    pass

  def add_simulation_results_postprocessing(self):
    self.actual_results = Simulation_results(self, actual=True)
    for i in range(0, self.number_simulations):
      self.simulation_results.append(Simulation_results(self, index=i))
    pass

  def prep_data(self, path):
    # placeholder function for now
    
    return None
  

  # my intuition is that I should be able to to both this and the other recursive bracket manipulation functions using callbacks I'm not familiar enough with Python to know how to. May come back to this
  def postprocess_bracket(self, bracket, criteria):
    self.postprocess_recursion(bracket.bracket, criteria)
    # bracket.bracket.root.postprocess_pick_team()
    pass
  
  def postprocess_recursion(self, node, criteria):
    # sorted DFS post order
    for child in node.children:
      # go through until there are no children
      if not hasattr(child.winner, 'name'):
        self.postprocess_recursion(child, criteria)
    # then sim game
    node.postprocess_pick_team(criteria)
    pass

  def export_teams_to_json(self):
    return json.dumps(self.all_teams, default=lambda o: o.toJSON(), sort_keys=True, ensure_ascii=False)

  def add_entry(self, entry):
    entry.index = len(self.entries["imported_entries"])
    self.entries["imported_entries"].append(entry)
    self.update_imported_entry_score(entry)
    # self.

  def add_bulk_entries_from_database(self, number_entries):
    current_path = os.path.dirname(__file__)
    database = r"..\\db\\"+self.gender+str(self.year)+".db"
    database_path = os.path.join(current_path, database)
    db = sqlite3.connect(database_path)
    current = db.cursor()
    pull_query = '''SELECT * FROM entries 
                      WHERE id IN 
                      (SELECT id FROM entries 
                      WHERE name <> 'NULL' 
                      ORDER BY RANDOM() 
                      LIMIT ?) '''
    data = tuple([number_entries])
    bulk_entries = current.execute(pull_query, data).fetchall()
    for entry in bulk_entries:
      # I don't feel great about the formatting used to add entries, Seems like
      # I should be passing in just the data instead of initializing an object 
      # here. trying to think of a better structure
      self.add_entry(Entry(method="database", source=entry))

  def update_special_entry_score(self, entry, entry_name):
    for region in self.all_teams:
        for seed in self.all_teams[region]:
          for team in self.all_teams[region][seed]:
            team.special_entries[entry_name] = entry.team_picks[team.region][team.seed][team.name]
            for i in range(0, len(team.simulation_results)):
              if len(entry.scores["simulations"]) <= i:
                entry.scores["simulations"].append(0)
              entry.scores["simulations"][i] += self.scoring_system["cumulative"][min(team.simulation_results[i], team.special_entries[entry_name])]
            entry.scores["actual_results"] += self.scoring_system["cumulative"][min(team.entry_picks["actual_results"], team.special_entries[entry_name])]
            # entry.scores["chalk"] += self.scoring_system["cumulative"][min(team.entry_picks["chalk"], team.entry_picks["imported_entries"][entry.index])]
            # entry.scores["most_valuable_teams"] += self.scoring_system["cumulative"][min(team.entry_picks["most_valuable_teams"], team.entry_picks["imported_entries"][entry.index])]
            # entry.scores["most_popular_teams"] += self.scoring_system["cumulative"][min(team.entry_picks["most_popular_teams"], team.entry_picks["imported_entries"][entry.index])]
            # print(team.name, team.simulation_results[0], team.entry_picks[entry.index], entry.scores[0])

  def update_imported_entry_score(self, entry):
    # update the scoring list for the passed in entry.
    # print('team name, sim results, entry results')
    for region in self.all_teams:
      for seed in self.all_teams[region]:
        for team in self.all_teams[region][seed]:
          while len(team.entry_picks["imported_entries"]) < entry.index+1:
            team.entry_picks["imported_entries"].append(-1)
          team.entry_picks["imported_entries"][entry.index] = entry.team_picks[team.region][team.seed][team.name]
          # print(team.name, team.simulation_results[0], )
          for i in range(0, len(team.simulation_results)):
            if len(entry.scores["simulations"]) <= i:
              entry.scores["simulations"].append(0)
            entry.scores["simulations"][i] += self.scoring_system["cumulative"][min(team.simulation_results[i], team.entry_picks["imported_entries"][entry.index])]
          entry.scores["actual_results"] += self.scoring_system["cumulative"][min(team.entry_picks["actual_results"], team.entry_picks["imported_entries"][entry.index])]
          # entry.scores["chalk"] += self.scoring_system["cumulative"][min(team.entry_picks["chalk"], team.entry_picks["imported_entries"][entry.index])]
          # entry.scores["most_valuable_teams"] += self.scoring_system["cumulative"][min(team.entry_picks["most_valuable_teams"], team.entry_picks["imported_entries"][entry.index])]
          # entry.scores["most_popular_teams"] += self.scoring_system["cumulative"][min(team.entry_picks["most_popular_teams"], team.entry_picks["imported_entries"][entry.index])]
          # print(team.name, team.simulation_results[0], team.entry_picks[entry.index], entry.scores[0])

  def output_results(self):
    average_winning_score = statistics.mean(self.winning_scores_of_simulations)
    a = {'winning_score': self.winning_scores_of_simulations,
         'most_valuable_score': self.special_entries["most_valuable_teams"].scores["simulations"]

         }

    b = df(data=a)
    print(b)
    # c = 
    plt.figure(1)
    d = plt.hist(b["winning_score"], bins=40, cumulative=True)
    plt.figure(2)
    c = b.plot(kind="scatter", x="winning_score", y="most_valuable_score")
    plt.show()
    print(average_winning_score)

class Bracket:
  def __init__(self, model, method="empty", source=None):
    self.game_pairing = 0
    self.model = model
    if method == "empty":
      self.bracket = self.create_bracket()
    elif method == "json":
      raise Exception("unknown method designated for bracket creation, creating empty bracket")
      # self.bracket = self.import_bracket_json(source)
    elif method == "url":
      raise Exception("unknown method designated for bracket creation, creating empty bracket")
      # self.bracket = self.import_bracket_url(source)
    else:
      raise Exception("unknown method designated for bracket creation, creating empty bracket")
      # self.bracket = create_bracket()
    pass

  def create_bracket(self):
    finals = NodeGame(region="Finals")#, model=self.model)
    for ff_pairings in final_four_pairings[self.model.gender][self.model.year]:
      finals.add_child(self.add_semis(ff_pairings))
    return finals
  
  def add_semis(self, pairing):
    # create top of bracket
    self.game_pairing = 0
    child_one = self.add_team(region=pairing[0], round_num=5)
    self.game_pairing = 0
    child_two = self.add_team(region=pairing[1], round_num=5)
    semi = NodeGame(region="Final Four", children=[child_one, child_two], round_num=6)
    return semi

  def add_team(self, region, round_num):
    if round_num == 2:
      seed_one = str(seed_pairings[self.game_pairing][0])
      seed_two = str(seed_pairings[self.game_pairing][1])
      team_one = self.model.all_teams[region][seed_one]
      team_two = self.model.all_teams[region][seed_two]
      if len(team_two) == 2:
        play_in = NodeGame(region=region, team_one=team_two[0], team_two=team_two[1],round_num=1)
        ro64 = NodeGame(region=region, team_one=team_one[0], children=play_in, round_num=round_num)
      else:
        ro64 = NodeGame(region=region, team_one=team_one[0], team_two=team_two[0], round_num=round_num)
      self.game_pairing += 1
      return ro64
    else:
      team_one = self.add_team(region=region, round_num=round_num-1)
      team_two = self.add_team(region=region, round_num=round_num-1)
      game = NodeGame(region=region, round_num=round_num, children=[team_one, team_two])
      return game
    pass

  def simulate_bracket(self):
    self.simulate_bracket_recursion(self.bracket)

    pass
  
  def simulate_bracket_recursion(self, node):
    # sorted DFS post order
    for child in node.children:
      # go through until there are no children
      if not hasattr(child.winner, 'name'):
        self.simulate_bracket_recursion(child)
    # then sim game
    node.simulate_game()
    pass

  def reset_bracket(self):
    # as it turns out is much more performant to just reset all the teams to 
    # blank rather than copying entire object
    placeholder_team = Team('tbd',0,'tbd',-1,-1)
    self.reset_bracket_recursion(self.bracket, placeholder_team)
    

  def reset_bracket_recursion(self, node, team):
    for child in node.children:
      if hasattr(child.winner, "name"):
        self.reset_bracket_recursion(child, team)
    node.winner = None
    if len(node.children) == 1:
      node.team_two = team
    elif len(node.children) == 2:
      node.team_one = team
      node.team_two = team


  def export_bracket_to_json(self, bracket, name):
    game_list = queue.SimpleQueue()
    results_list = {}
    for region in self.model.all_teams:
      results_list[region] = {}
      for seed in self.model.all_teams[region]:
        results_list[region][seed] = {}
        for team in self.model.all_teams[region][seed]:
          results_list[region][seed][team.name] = -1
    winner = bracket.root.winner
    results_list[winner.region][winner.seed][winner.name] = 7
    game_list.put(bracket.root)
    while game_list.qsize() != 0:
      current_game = game_list.get()
      temp_region = current_game.team_one.region
      temp_seed = current_game.team_one.seed
      temp_name = current_game.team_one.name
      if results_list[temp_region][temp_seed][temp_name] == -1:
        results_list[temp_region][temp_seed][temp_name] = current_game.round_num - 1
      temp_region = current_game.team_two.region
      temp_seed = current_game.team_two.seed
      temp_name = current_game.team_two.name
      if results_list[temp_region][temp_seed][temp_name] == -1:
        results_list[temp_region][temp_seed][temp_name] = current_game.round_num - 1
      for child in current_game.children:
        game_list.put(child)
    results = {}
    results["team_picks"] = results_list
    results["name"] = name
    results["method"] = "json"
    results["entryID"] = None
    results["source"] = None
    a = json.dumps(results)
    return a

  def import_bracket_url(self):
    pass


class Team:
  def __init__(self, name, seed, region, elo, picked_frequency):
    self.name = name
    self.seed = seed
    self.region = region
    self.elo = elo
    self.picked_frequency = picked_frequency

    self.wins = {
      # round number is key, value is number of wins
      1:0, 
      2:0, 
      3:0, 
      4:0, 
      5:0, 
      6:0, 
      7:0, 
    }
    self.expected_points = {
      # round number is key, value is number of expected points
      1:0, 
      2:0, 
      3:0, 
      4:0, 
      5:0, 
      6:0, 
      7:0, 
    }
    self.simulation_results = []
    self.temp_result = 0
    self.total_expected_points = 0
    self.entry_picks = {
      "imported_entries" : [],
      "actual_results" : 0,
      # "most_valuable_teams" : 0,
      # "most_popular_teams" : 0,
      # "chalk" : 0
    }
    self.special_entries = {
      "most_valuable_teams": None,
      "most_popular_teams": None,
      "chalk": None,
    }
    pass

  def __str__(self):
    return str(self.seed)+" "+str(self.name)+ " "+str(self.elo)+" EP: "+str(self.total_expected_points)

  def __repr__(self):
    # return "Name: "+str(self.name)+"\nseed: "+str(self.seed)+"\nRegion: "+str(self.region)+"\nRating: "+str(self.elo)
    return str(self.seed)+" "+str(self.name)+ " "+str(self.elo)

  def update_elo(self, team_two, winner):
    # update elo for future rounds based on game outcome. not sure how to do this for now so no update to elo will occur
    pass

  def toJSON(self):
    export_data = {
        "name" : self.name,
      "seed" : self.seed,
      "region" : self.region,
      "elo" : self.elo,
      "picked_frequency" : self.picked_frequency,
      "wins" : self.wins,
      "expected_points" : self.expected_points,
      "total_expected_points" : self.total_expected_points,
    }
    return export_data

class Game:
  # placeholder base class used as anytree implementation requires
  pass

class NodeGame(Game, NodeMixin):
  def __init__(self, team_one=Team('tbd',0,'tbd',-1,-1), team_two=Team('tbd',0,'tbd',-1,-1), parent=None, winner=None, children=None, region=None, round_num=7):
    super(NodeGame, self).__init__()
    self.team_one = team_one
    self.team_two = team_two
    self.parent = parent
    # self.model = model
    if parent:
      self.round_num = parent.round_num - 1
    else:
      self.round_num = round_num
    self.winner = winner
    if children:
      self.add_child(children)
    if region:
      self.region = region
    self.name = self.__str__()

  def __str__(self):
    return "R"+str(self.round_num)+" in the "+str(self.region)+" Region between "+str(self.team_one)+" and "+str(self.team_two)+"."

  def __repr__(self):
    if self.winner:
      return "R"+str(self.round_num)+" in the "+str(self.region)+" w/ "+str(self.team_one)+" vs "+str(self.team_two)+".  Winner is "+str(self.winner)
    else:
      return "R"+str(self.round_num)+" in the "+str(self.region)+" w/ "+str(self.team_one)+" vs "+str(self.team_two)+"."

  def toJSON(self):
    exporter = JsonExporter(sort_keys=True, default=lambda o: o.toJSON())
    # c = exporter.export(self.root)
    return exporter.export(self.root)

  def simulate_game(self):
    # simulate the outcome of the game using 538's ELO system ( sans travel adjustment)
    # as seen here https://fivethirtyeight.com/methodology/how-our-march-madness-predictions-work-2/

    # make sure the game doesn't already have a winner
    assert not self.winner, "game between "+str(self.team_one)+" and  "+str(self.team_two)+" already has been played."
    team_one_chance = 1.0/(1.0 + pow(10,(-(self.team_one.elo-self.team_two.elo))*30.464/400))
    if random.random() < team_one_chance:
      # team one wins
      winner = self.team_one
      self.team_one.update_elo(self.team_two, True)
      self.team_two.update_elo(self.team_one, False)
    else:
      # team two wins
      winner = self.team_two
      self.team_one.update_elo(self.team_two, False)
      self.team_two.update_elo(self.team_one, True)
    # pass
    self.update_bracket(winner)
    self.update_wins(model, self.winner, self.round_num)

  def update_wins(self, bracket, winner, round_number):
    teams = bracket.all_teams[winner.region][winner.seed]
    if len(teams)==1:
      team = teams[0]
      # if there was no play in game, increment round one win total to keep it aligned
      if round_number == 2:
        team.wins[1]  = bracket.number_simulations
    else:
      if teams[0].name == winner.name:
        team = teams[0]
      else:
        team = teams[1]
    team.wins[round_number] += 1
    team.temp_result = round_number
    pass

  def update_bracket(self, winning_team):
    # update bracket with results of game
    assert not self.winner, "game between "+str(self.team_one)+" and  "+str(self.team_two)+" already has been played."
    self.winner = winning_team
    if self.parent:
      if self.parent.team_one.name == "tbd":
        self.parent.team_one = winning_team 
      elif self.parent.team_two.name == "tbd":
        self.parent.team_two = winning_team
      else:
        raise Exception("both teams in parent exist: "+self.parent.team_one+" "+self.parent.team_two)
    pass
  
  def add_child(self, child):
    if type(child) is list:
      for i in child:
        i.parent = self
    else:
      child.parent = self
    pass

  def postprocess_pick_team(self, criteria):
    # between two teams in a matchup, pick the team with more of the given criteria. Used to visualize results
    if getattr(self.team_one, criteria)[self.round_num] > getattr(self.team_two, criteria)[self.round_num]:
      self.update_bracket(self.team_one)
    elif getattr(self.team_one, criteria)[self.round_num] < getattr(self.team_two, criteria)[self.round_num]:
      self.update_bracket(self.team_two)
    else:
      print("Teams "+self.team_one.name+" and "+self.team_two.name+" have the same "+criteria)
      if random.random() < 0.5:
        self.update_bracket(self.team_one)
      else:
        self.update_bracket(self.team_two)
    
class Entry:
  def __init__(self, method, source):
    if method == "empty":
      raise Exception("unknown method designated for bracket creation")
    elif method == "json":
      self.import_entry_json(source)
    
    elif method == "url":
      self.import_entry_url(source)
    elif method == "database":
      self.import_entry_database(source)
    else:
      raise Exception("unknown method designated for bracket creation")
      # self.bracket = create_bracket()
    
    self.index = 0
    self.scores = {
      "simulations" : [],
      "actual_results" : 0,
      "most_valuable_teams" : 0,
      "most_popular_teams" : 0,
      "chalk" : 0
    }
    # model.add_entry(self)

  def import_entry_json(self, source):
    b = json.loads(source)
    self.name = b["name"]
    self.entryID = b["entryID"]
    self.method = b["method"]
    self.team_picks = b["team_picks"]
    self.source = b["source"]
    pass

  def import_entry_database(self, source):
    self.name = source[1]
    self.team_picks = self.assign_team_picks_from_database(source) 
    self.entryID = source[0]
    self.method = "database"
    pass

  def assign_team_picks_from_database(self, source):
    team_data = r'..\\team_data\\team_'+model.gender+str(model.year)+'_20200407_0840.json'
    current_path = os.path.dirname(__file__)
    new_team_data = os.path.join(current_path, team_data)
    teams = json.load(open(new_team_data, "r"))
    i=6
    team_picks = {}
    for region in teams:
      team_picks[region] = {}
      for seed in teams[region]:
        team_picks[region][seed] = {}
        for team in teams[region][seed]:
          team_picks[region][seed][team["name"]] = source[i]
          i += 1
    return team_picks

class Simulation_results:
  def __init__(self, model, actual=False, index=-1):
    self.model = model
    self.simulation_index = index
    self.actual = actual
    self.score_list = {
      "entries" : [],
      # "actual_results" : 0,
      "most_valuable_teams" : 0,
      "most_popular_teams" : 0,
      "chalk" : 0
    }
    self.winning_score = 0
    self.winning_index = []
    self.beaten_by = {
      # "actual_results" : False,
      "most_valuable_teams" : False,
      "most_popular_teams" : False,
      "chalk" : False
    }

    self.number_of_entries = len(self.model.entries["imported_entries"])
    self.import_scoring_list()

  def import_scoring_list(self):
    entry_results = []
    winning_score = 0
    winning_index = [-1]
    most_valuable_team_score = 0
    chalk_score = 0
    most_popular_team_score = 0
    # Populate imported entry scores
    for entry in self.model.entries["imported_entries"]:
      if self.actual:
        entry_results.append(entry.scores["actual_results"])
      else:
        entry_results.append(entry.scores["simulations"][self.simulation_index])
      if entry_results[-1] > winning_score:
        winning_score = entry_results[-1]
        winning_index = [len(entry_results) - 1]
      elif entry_results[-1] == winning_score:
        winning_index.append(len(entry_results) - 1)
        # print("tied winning brackets in simulation: "+str(self.simulation_index))
    
    # Populate special bracket scores
    if self.actual:
      most_valuable_team_score = self.model.special_entries["most_valuable_teams"].scores["actual_results"]
      most_popular_team_score = self.model.special_entries["most_popular_teams"].scores["actual_results"]
      chalk_score = self.model.special_entries["chalk"].scores["actual_results"]
    else:
      most_valuable_team_score = self.model.special_entries["most_valuable_teams"].scores["simulations"][self.simulation_index]
      most_popular_team_score = self.model.special_entries["most_popular_teams"].scores["simulations"][self.simulation_index]
      chalk_score = self.model.special_entries["chalk"].scores["simulations"][self.simulation_index]
    self.scoring_list = {
      "entries" : entry_results,
      # "actual_results" : 0,
      "most_valuable_teams" : most_valuable_team_score,
      "most_popular_teams" : most_popular_team_score,
      "chalk" : chalk_score
    }
    for criteria in self.beaten_by:
      if self.scoring_list[criteria] >= winning_score:
        self.beaten_by[criteria] = True
        # print(criteria+" would have won simulation "+str(self.simulation_index))
        self.model.simulations_won_by_special_entries[criteria] += 1
    self.winning_score = winning_score
    self.winning_index = winning_index
    if not self.actual:
      self.model.winning_scores_of_simulations.append(winning_score)
      if len(self.model.simulations_won_by_imported_entries) != len(self.model.entries["imported_entries"]):
        for j in range(0,len(self.model.entries["imported_entries"])):
          self.model.simulations_won_by_imported_entries.append(0)
      for i in winning_index:
        self.model.simulations_won_by_imported_entries[i] += 1




# Holding a main function removes the global scoping I was using to call 
# the model I'm scoring various brackets. I'd like to rearrange this in some way
# but need to think on how.
# def main():

# t=time.time()
model = Model(number_simulations=1000, scoring_system=scoring_systems["degen_bracket"])
model.batch_simulate()
model.update_entry_picks()
model.initialize_special_entries()
model.analyze_special_entries()

model.add_bulk_entries_from_database(15)
model.add_simulation_results_postprocessing()
model.output_results()
# t = time.time() - t

print("done")


# if __name__ == '__main__':
#   main()