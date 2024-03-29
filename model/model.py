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
import random

# Final four pairings
final_four_pairings = {
  "mens" : {
    2024 : 
      [['East', 'West'],
      ['South', 'Midwest']]
    ,
    2021 : 
      [['West', 'East'],
      ['South', 'Midwest']]
    ,
    2019 : 
      [['East', 'West'], 
      ['South', 'Midwest']]
    ,
    2018 : {
      # TBD
    }
  },
  "womens" : {
    2021 : 
      [['Alamo, Hemisfair'],
      ['River Walk', 'Mercado']]
    ,
    2019 : 
      [["Greensboro", "Portland"],
      ["Chicago", "Albany"]]
    ,
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
  },

    "pick_six" : {
    "round" : {
      0 : 0,
      1 : 0,
      2 : 1,
      3 : 1,
      4 : 1,
      5 : 1,
      6 : 1,
      7 : 7,
    },
    "cumulative" : {
      0 : 0,
      1 : 0,
      2 : 1,
      3 : 2,
      4 : 3,
      5 : 4,
      6 : 5,
      7 : 12,
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
  def __init__(self, gender='mens', year=2021, number_simulations=1, scoring_sys="degen_bracket"):
    self.gender = gender
    self.year = year 
    self.all_teams = self.create_teams()
    self.start_bracket = Bracket(model=self)
    self.sim_bracket = Bracket(model=self)
    self.bracket_pairings = final_four_pairings[gender][year]
    self.game_pairing = 0
    self.number_simulations = number_simulations
    self.completed_simulations = 0
    self.scoring_system = scoring_systems[scoring_sys]

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
      "most_valuable_teams": None,
      "most_popular_teams": None,
      "chalk": None,
    }
    self.simulations_won_by_imported_entries = []
    self.winning_scores_of_simulations = []
    pass

  def raw_print(self):
    for region in sorted(self.all_teams.keys()):
      for seed in sorted(self.all_teams[region].keys(), key=lambda x: int(x)):
        for team in self.all_teams[region][seed]:
          print(team.name+", "+team.region+", "+team.seed+", "+str(team.total_expected_points)+", "+str(team.total_picked_expected_points)+", "+str(team.total_points_diff)+", "+str(", ".join(str(value) for value in team.wins.values())))



  def create_teams(self):
    current_path = os.path.dirname(__file__)
    team_data = "../team_data/"+str(self.year)+"_all_prepped_data.csv"
    path = os.path.join(current_path, team_data)

    
    all_teams = {}
    if os.path.exists(path):
      print(" found data")
      
    else:
      print(" couldn't find data")
      # In original iterations of this I would've attached scraping natively to 
      # this but now I don't think that that really makes sense
      raise Exception("There is no data for this combination of team and year")

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
      team_seed = str(df["team_seed"][ind])
      # team seeds in the imported file have an a or B suffix for playin games, 
      # this strips that 
      # todo uncomment this and repull all data once playins are played
      # if len(team_seed) > 2:
      #   team_seed = team_seed[0:2]
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
      self.sim_bracket.simulate_bracket()
      self.update_scores()
      self.reset_bracket()
      self.completed_simulations += 1
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
          total_picked_expected_points = 0
          total_points_diff = 0
          for ep in team.expected_points:
            round_expected_points = float(team.wins[ep]) / float(self.number_simulations) * float(self.scoring_system["round"][ep])
            picked_round_expected_points = float(team.picked_frequency[ep].strip('%'))/100 * float(self.scoring_system["round"][ep])
            round_points_diff = round_expected_points - picked_round_expected_points
            team.expected_points[ep] = round_expected_points
            team.picked_expected_points[ep] = picked_round_expected_points
            team.points_diff[ep] = round_points_diff
            total_expected_points += round_expected_points
            total_picked_expected_points += picked_round_expected_points
            total_points_diff += round_points_diff
          team.total_expected_points = total_expected_points
          team.total_picked_expected_points = total_picked_expected_points
          team.total_points_diff = total_points_diff
    pass

  def output_most_valuable_bracket(self):
    # TODO this can be exported into JSON format without going into the intermediate bracket step
    self.calculate_expected_points()
    most_valuable_bracket = Bracket(self)
    self.postprocess_bracket(most_valuable_bracket, "expected_points")
    return most_valuable_bracket

  def output_random_bracket(self):
    # TODO this can be exported into JSON format without going into the intermediate bracket step
    # self.calculate_expected_points()
    random_bracket = Bracket(self)
    self.postprocess_bracket(random_bracket, "randomized")
    return random_bracket

  def output_most_popular_bracket(self):
    # TODO this can be exported into JSON format without going into the intermediate bracket step
    most_popular_bracket = Bracket(self)
    self.postprocess_bracket(most_popular_bracket, "picked_frequency")
    return most_popular_bracket

  def update_entry_picks(self):
    team_data = r'../web_scraper/'+self.gender+str(self.year)+r'/actual.json'
    # chalk_data = r'../web_scraper/'+model.gender+str(model.year)+r'/chalk.json'
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
          else:
            self.all_teams[region][seed][1].entry_picks["actual_results"] = actual_results[region][seed][team]
    entry = {
      "team_picks" : actual_results,
      "name" : "Actual results",
      "entryID" : -1,
      "method" : "Actual results",
      "source" : "Actual results"
    }
    self.entries["actual_results"] = Entry(model=self, source=json.dumps(entry), method="json")

  def initialize_special_entries(self):
    # Initialize the special entries including:
    # Most valuable bracket, most popular bracket, chalk bracket
    most_valuable_bracket = self.output_most_valuable_bracket()
    most_popular_bracket = self.output_most_popular_bracket()
    # random_bracket = self.output_random_bracket()
    current_path = os.path.dirname(__file__)
    chalk_data = r'../web_scraper/'+self.gender+str(self.year)+r'/chalk.json'
    chalk_team_data = os.path.join(current_path, chalk_data)
    chalk_results = json.load(open(chalk_team_data, "r"))
    chalk_entry = {
      "team_picks" : chalk_results,
      "name" : "Chalk entry",
      "entryID" : -4,
      "method" : "Chalk entry",
      "source" : "Chalk entry"
    }
    mvb_source = self.sim_bracket.export_bracket_to_json(most_valuable_bracket.bracket.root, "most valuable bracket")
    mpb_source = self.sim_bracket.export_bracket_to_json(most_popular_bracket.bracket.root, "most popular bracket")
    # random_bracket = self.sim_bracket.export_bracket_to_json(random_bracket.bracket.root, "random bracket")
    self.special_entries["most_valuable_teams"] = Entry(model=self, source=mvb_source, method="json")
    self.special_entries["most_popular_teams"] = Entry(model=self, source=mpb_source, method="json")
    self.special_entries["chalk"] = Entry(model=self, source=json.dumps(chalk_entry), method="json")

  def analyze_special_entries(self):
    # Add in the results for special brackets including:
    # Most valuable bracket, most popular bracket, chalk bracket
    for entry in self.special_entries:
      self.update_special_entry_score(self.special_entries[entry], entry)

  def postprocess_via_popularity_and_value(self):
    # Add most valuable and most picked brackets
    most_valuable_bracket = self.output_most_valuable_bracket()
    most_popular_bracket = self.output_most_popular_bracket()
    mvb_source = self.sim_bracket.export_bracket_to_json(most_valuable_bracket.bracket.root, "most valuable bracket")
    mpb_source = self.sim_bracket.export_bracket_to_json(most_popular_bracket.bracket.root, "most popular bracket")
    self.entries["most_valuable_teams"] = Entry(source=mvb_source, method="json")
    self.update_special_entry_score(self.entries["most_valuable_teams"])
    self.entries["most_popular_teams"] = Entry(source=mpb_source, method="json")
    
    pass

  def add_simulation_results_postprocessing(self):
    self.actual_results = Simulation_results(self, actual=True)
    if len(self.simulation_results) == 0:
      for i in range(0, self.number_simulations):
        self.simulation_results.append(Simulation_results(self, index=i))
    pass

  def refresh_scoring_list(self):
    for simulation in self.simulation_results:
      simulation.import_scoring_list()

  def prep_data(self, path):
    # Probably never going to use this
    return None
  

  # my intuition is that I should be able to to both this and the other 
  # recursive bracket manipulation functions using callbacks I'm not familiar 
  # enough with Python to know how to. May come back to this
  def postprocess_bracket(self, bracket, criteria):
    self.postprocess_recursion(bracket.bracket, criteria)
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

  def export_teams_to_json(self, expanded=True, empty=False, array=True):
    if expanded:
      return json.dumps(self.all_teams, default=lambda o: o.toJSON(array), sort_keys=True, ensure_ascii=False)
    else:
      return json.dumps(self.all_teams, default=lambda o: o.toJSON(expanded=False, empty=empty), sort_keys=True, ensure_ascii=False)


  def add_entry(self, entry):
    entry.index = len(self.entries["imported_entries"])
    self.entries["imported_entries"].append(entry)
    self.update_imported_entry_score(entry)
    # self.

  def add_fake_entries(self, number_entries):
    for i in range(number_entries):
      random_bracket = self.output_random_bracket()
      random_bracket = self.sim_bracket.export_bracket_to_json(random_bracket.bracket.root, "random bracket no."+str(i+1),entryID=i+1)
      self.add_entry(Entry(model=self, source=random_bracket, method="json"))
    pass

  # TODO Make this incremental potentially
  def add_bulk_entries_from_database(self, number_entries):
    current_path = os.path.dirname(__file__)
    database = r"../db/"+self.gender+str(self.year)+".db"
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
      self.add_entry(Entry(model=self, method="database", source=entry))
    self.refresh_scoring_list()

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

  def update_imported_entry_score(self, entry):
    # update the scoring list for the passed in entry.
    for region in self.all_teams:
      for seed in self.all_teams[region]:
        for team in self.all_teams[region][seed]:
          while len(team.entry_picks["imported_entries"]) < entry.index+1:
            team.entry_picks["imported_entries"].append(-1)
          team.entry_picks["imported_entries"][entry.index] = entry.team_picks[team.region][team.seed][team.name]
          for i in range(0, len(team.simulation_results)):
            if len(entry.scores["simulations"]) <= i:
              entry.scores["simulations"].append(0)
            entry.scores["simulations"][i] += self.scoring_system["cumulative"][min(team.simulation_results[i], team.entry_picks["imported_entries"][entry.index])]
          entry.scores["actual_results"] += self.scoring_system["cumulative"][min(team.entry_picks["actual_results"], team.entry_picks["imported_entries"][entry.index])]

  # Output is a data frame which has the simulation results for each entry as well
  # as the special entries
  # Todo The general structuring of outputting of results, especially the sorting
  # of ranks is pretty inefficient. This would be a potential place to really 
  # improve the efficiency of the program.
  def output_results(self, entries=None, sims=None):
    # output_results is used both For initial rankings and also for further 
    # postprocessing of subsets. Initial rankings are already ranked and so I 
    # don't want to go through the trouble of doing that again.  
    # The initial_ranking variables a boolean to check whether this is the 
    # first time things are ranked.
    initial_ranking=True
    if not entries:
      entry_list = self.entries['imported_entries']
      entry_index_list = [i for i in range(len(entry_list))]
    else:
      entry_list = random.sample(self.entries['imported_entries'], entries)
      entry_index_list = [entry.index for entry in entry_list]
      initial_ranking = False

    if not sims:
      simulation_list = self.simulation_results
      sim_index_list = [i for i in range(len(simulation_list))]
    else:
      simulation_list = random.sample(self.simulation_results, sims)
      sim_index_list = [sim.simulation_index for sim in simulation_list]
      initial_ranking = False

    def add_data_frame_entry(entryID, name, array_name, sim_index_list):
      all_team_data['entryID'].append(entryID)
      all_team_data['name'].append(name)
      simulation_results = []
      for sim in sim_index_list:
        simulation_results.append(array_name[sim])
      all_team_data['simulations'].append(simulation_results)

    def add_rankings():
      all_team_data['ranks'] = [[] for i in range(len(all_team_data['simulations']))]
      all_team_data['placings'] = [[] for i in range(len(all_team_data['simulations']))]
      if entries and sims:
        print(" subset ")
      else:
        for simulation in simulation_list:
          for i in entry_index_list:
            all_team_data['ranks'][i].append(simulation.ranking_list['entries'][i])
            all_team_data['placings'][i].append(simulation.placing_list['entries'][i])
          all_team_data['ranks'][len(entry_list)].append(1.0)
          all_team_data['ranks'][len(entry_list)+1].append(simulation.ranking_list['most_valuable_teams'])
          all_team_data['ranks'][len(entry_list)+2].append(simulation.ranking_list['most_popular_teams'])
          all_team_data['ranks'][len(entry_list)+3].append(simulation.ranking_list['chalk'])
          all_team_data['placings'][len(entry_list)].append(1)
          all_team_data['placings'][len(entry_list)+1].append(simulation.placing_list['most_valuable_teams'])
          all_team_data['placings'][len(entry_list)+2].append(simulation.placing_list['most_popular_teams'])
          all_team_data['placings'][len(entry_list)+3].append(simulation.placing_list['chalk'])

    def rerank(entry_list):
      # Use ranking algorithm for limited scoring data set
      all_team_data['ranks'] = [[] for i in range(len(entry_list)+4)]
      all_team_data['placings'] = [[] for i in range(len(entry_list)+4)]
      winning_score_list = []
      winning_index_list = []
      winning_score = 0
      winning_index = [-1]

      for simulation in simulation_list:
        array = [entry.scores['simulations'][simulation.simulation_index] for entry in entry_list]
        special_scores = {
          'scores' : {
            'most_valuable_teams' : simulation.scoring_list['most_valuable_teams'],
            'most_popular_teams' : simulation.scoring_list['most_popular_teams'],
            'chalk' : simulation.scoring_list['chalk'],
          },
          'ranks' : {
            'most_valuable_teams' : -1.0,
            'most_popular_teams' : -1.0,
            'chalk' : -1.0,
          },
          'placings' : {
            'most_valuable_teams' : -1,
            'most_popular_teams' : -1,
            'chalk' : -1,
          }
        }
        rank_vector = [0 for i in range(len(array))]
        placing_vector = [0 for i in range(len(array))]
        tuple_array = [(array[i], i) for i in range(len(array))]
        tuple_array.sort(reverse=True)
        winning_score = tuple_array[0][0]
        # all_team_data['simulations'][len(entry_list)] = winning_score
        winning_index = [entry_list[tuple_array[0][1]].index]
        (rank, n, i) = (1, 1, 0)

        for special in special_scores['scores'].keys():
          if special_scores['scores'][special] > winning_score:
            special_scores['ranks'][special] = 1.0
            special_scores['placings'][special] = 1
          elif special_scores['scores'][special] < tuple_array[-1][0]:
            special_scores['ranks'][special] = float(len(tuple_array))
            special_scores['placings'][special] = len(tuple_array)
        while i < len(array):
          j = i
          while j < len(array) - 1 and tuple_array[j][0] == tuple_array[j+1][0]:
            j += 1
            if tuple_array[j][0] == winning_score:
              winning_index.append(entry_list[tuple_array[j][1]].index)
          n = j - i + 1
          for j in range(n):
            shared_index = tuple_array[i+j][1]
            rank_vector[shared_index] = rank + (n - 1) * 0.5
            placing_vector[shared_index] = rank
          for special in special_scores['scores'].keys():
            if special_scores['scores'][special] == tuple_array[i+j][0]:
              special_scores['ranks'][special] = rank_vector[shared_index]
              special_scores['placings'][special] = rank
            elif special_scores['scores'][special] < tuple_array[i][0] and special_scores['scores'][special] > tuple_array[i-1][0]:
              assert tuple_array[i][0]>=tuple_array[i-1][0]
              special_scores['ranks'][special] = rank_vector[shared_index]
              special_scores['placings'][special] = rank
          rank += n
          i += n
        
        
        for special in special_scores['scores'].keys():
          if special_scores['scores'][special] > winning_score:
            special_scores['ranks'][special] = 1.0
            special_scores['placings'][special] = 1
            # print("a",special, special_scores['ranks'][special], special_scores['scores'][special])
          elif special_scores['scores'][special] < tuple_array[-1][0]:
            special_scores['ranks'][special] = float(len(tuple_array))
            special_scores['placings'][special] = len(tuple_array)
            # print("b",special, special_scores['ranks'][special], special_scores['scores'][special])
          elif special_scores['scores'][special] == winning_score:
            special_scores['ranks'][special] = rank_vector[tuple_array[0][1]]
            special_scores['placings'][special] = placing_vector[tuple_array[0][1]]
            # print("c",special, special_scores['ranks'][special], special_scores['scores'][special])
          else:
            i = 1
            while i < len(tuple_array):
              if tuple_array[i-1][0] > special_scores['scores'][special] > tuple_array[i][0]:
                multiples = 0
                while tuple_array[i+multiples][0] == tuple_array[i][0] and i < len(tuple_array):
                  multiples +=1
                  if i+multiples == len(tuple_array):
                    break
                special_scores['ranks'][special] = i+(multiples-1)*0.5+1
                special_scores['placings'][special] = i+1
                # print("d",i,special, special_scores['ranks'][special], special_scores['scores'][special])
                i = len(tuple_array)
                
              elif special_scores['scores'][special] == tuple_array[i][0]:
                special_scores['ranks'][special] = rank_vector[tuple_array[i][1]]
                special_scores['placings'][special] = placing_vector[tuple_array[i][1]]
                # print("e",i,special, special_scores['ranks'][special], special_scores['scores'][special])
                i = len(tuple_array)
              else:
                i += 1

        for special in special_scores['scores'].keys():
          assert special_scores['ranks'][special] > 0
          assert not (special_scores['ranks'][special] == 1 and special_scores['scores'][special] < winning_score and len(array)>1)
        for i in range(len(entry_list)):
          all_team_data['ranks'][i].append(rank_vector[i])
          all_team_data['placings'][i].append(placing_vector[i])
        winning_score_list.append(winning_score)
        winning_index_list.append(winning_index)
        all_team_data['simulations'][len(entry_list)] = winning_score_list
        all_team_data['ranks'][len(entry_list)].append(1.0)
        all_team_data['placings'][len(entry_list)].append(1)
        all_team_data['ranks'][len(entry_list)+1].append(special_scores['ranks']['most_valuable_teams'])
        all_team_data['placings'][len(entry_list)+1].append(special_scores['placings']['most_valuable_teams'])
        all_team_data['ranks'][len(entry_list)+2].append(special_scores['ranks']['most_popular_teams'])
        all_team_data['placings'][len(entry_list)+2].append(special_scores['placings']['most_popular_teams'])
        all_team_data['ranks'][len(entry_list)+3].append(special_scores['ranks']['chalk'])
        all_team_data['placings'][len(entry_list)+3].append(special_scores['placings']['chalk'])

    # Update winning scores
    all_team_data = {
      'entryID' : [],
      'name' : [],
      'simulations' : [],
      # 'ranks' : [],
      # 'placings' : []
    }
    for entry in entry_list:
      add_data_frame_entry(entry.entryID, entry.name, entry.scores['simulations'], sim_index_list)
    add_data_frame_entry(-1, 'winning_score', self.winning_scores_of_simulations, sim_index_list)
    add_data_frame_entry(-2, 'most_valuable_teams', self.special_entries['most_valuable_teams'].scores['simulations'], sim_index_list)
    add_data_frame_entry(-3, 'most_popular_teams', self.special_entries['most_popular_teams'].scores['simulations'], sim_index_list)
    add_data_frame_entry(-4, 'chalk', self.special_entries['chalk'].scores['simulations'], sim_index_list)
    if initial_ranking:
      add_rankings()
    else:
      rerank(entry_list)
    output_data = df(data=all_team_data)
    return output_data

  def get_special_wins(self):
    return self.simulations_won_by_special_entries

  # Helper functions for creating json files necessary.  Shouldn't be used except
  # when preparing another year's data.
  def create_json_files(self):
    current_path = os.path.dirname(__file__)
    json_connector = r"../web_scraper/"+self.gender+str(self.year)+r"/"
    json_path = os.path.join(current_path, json_connector)
    if not os.path.exists(json_path+"chalk.json"):
      print("writing chalk.json file.")
      chalk = self.export_teams_to_json(expanded=False)
      chalk = chalk.replace("[","")
      chalk = chalk.replace("]","")
      with open(json_path+"chalk.json", "w") as chalk_file:
        json.dump(json.loads(chalk), chalk_file)
        print('''Note: you must fill in the overall number one and number two seeds yourself.
                  \nIf this is for the men's bracket, you must update the play in teams (losers of the play in game have zero wins instead of one)''')
    if not os.path.exists(json_path+"empty.json"):
      print("writing empty.json file.")
      empty = self.export_teams_to_json(expanded=False, empty=True)
      empty = empty.replace("[","")
      empty = empty.replace("]","")
      empty = empty.replace("}, {", ", ") 
      empty = json.loads(empty)
      with open(json_path+"empty.json", "w") as empty_file:
        json.dump(empty, empty_file)
        print('''Note: If this is for the men's bracket, you must update the play in teams (losers of the play in game has zero wins instead of one)''')
    if not os.path.exists(json_path+"reverse_lookup.json"):
      print("writing reverse_lookup.json file.")
      with open(json_path+"empty.json", "r") as empty_file:
        empty = json.load(empty_file)
        reverse = {}
        for region in empty:
          for seed in empty[region]:
            for team in empty[region][seed]:
              reverse[team] = {
                "region" : region,
                "seed" : seed,
                "team" : team
              }
        with open(json_path+"reverse_lookup.json", "w") as reverse_file:
          json.dump(reverse, reverse_file)
    if not os.path.exists(json_path+"actual.json"):
      raise Exception("The 'actual.json' file is missing, you must fill it out yourself.")
    if not os.path.exists(json_path+"preliminary_results.json"):
      print("writing preliminary_results.json file.")
      preliminary = self.export_teams_to_json(array=True)
      with open(json_path+"preliminary_results.json", "w") as preliminary_file:
        json.dump(json.loads(preliminary), preliminary_file)
    pass

  def analyze_sublist(self, all_results, entries, sims):
    print(entries, sims)
    return self.output_results(entries, sims)

  # Get entry and return it based on entry ID
  def get_entry(self, entryID):
    if entryID > 0:
      for entry in self.entries['imported_entries']:
        if entry.entryID == entryID: 
          return entry
    else:
      for entry in self.special_entries:
        if self.special_entries[entry].entryID == entryID:
          return self.special_entries[entry]
    raise Exception("There is no data for this entry ID.")
    return None

class Bracket:
  def __init__(self, model, method="empty", source=None):
    self.game_pairing = 0
    self.model = model
    if method == "empty":
      self.bracket = self.create_bracket()
    # These methods could be used in the future but are not necessary right now
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

# Workflow is to create the finals node, add the two semi final nodes 
# in a small for loop, And then create each individual region recursively.
  def create_bracket(self):
    finals = NodeGame(region="Finals", model=self.model)
    for ff_pairings in final_four_pairings[self.model.gender][int(self.model.year)]:
      finals.add_child(self.add_semis(ff_pairings))
    return finals
  
  def add_semis(self, pairing):
    # create top of bracket
    self.game_pairing = 0
    child_one = self.add_team(region=pairing[0], round_num=5)
    self.game_pairing = 0
    child_two = self.add_team(region=pairing[1], round_num=5)
    semi = NodeGame(model=self.model, region="Final Four", children=[child_one, child_two], round_num=6)
    return semi

  def add_team(self, region, round_num):
    if round_num == 2:
      seed_one = str(seed_pairings[self.game_pairing][0])
      seed_two = str(seed_pairings[self.game_pairing][1])
      team_one = self.model.all_teams[region][seed_one]
      team_two = self.model.all_teams[region][seed_two]
      if len(team_two) == 2:
        play_in = NodeGame(model=self.model, region=region, team_one=team_two[0], team_two=team_two[1],round_num=1)
        ro64 = NodeGame(model=self.model, region=region, team_one=team_one[0], children=play_in, round_num=round_num)
      else:
        ro64 = NodeGame(model=self.model, region=region, team_one=team_one[0], team_two=team_two[0], round_num=round_num)
      self.game_pairing += 1
      return ro64
    else:
      team_one = self.add_team(region=region, round_num=round_num-1)
      team_two = self.add_team(region=region, round_num=round_num-1)
      game = NodeGame(model=self.model, region=region, round_num=round_num, children=[team_one, team_two])
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


  def export_bracket_to_json(self, bracket, name, entryID=None):
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
    results["entryID"] = entryID
    results["source"] = None
    # Hooking up entry IDs to special brackets to make them easier to find 
    # later for Dash postprocessing
    if name == 'most valuable bracket':
      results['entryID'] = -2
    elif name == 'most popular bracket':
      results['entryID'] = -3
    a = json.dumps(results)
    return a

  def import_bracket_url(self):
    pass

# The team object. In general a big concern I have is that some data that is 
# held in each of these objects should probably be held in entry or simulation 
# object instead.  At this point is probably too late to change anything but 
# probably a good lesson learned for the future.
class Team:
  def __init__(self, name, seed, region, elo, picked_frequency):
    self.name = name
    self.seed = seed
    self.region = region
    self.elo = float(elo)
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

    self.picked_expected_points = {
      # round number is key, value is picked_frequency * point value
      1:0, 
      2:0, 
      3:0, 
      4:0, 
      5:0, 
      6:0, 
      7:0, 
    }

    self.points_diff = {
      # round number is key, value is expected points - picked expected points -> high value = "underpicked" teams
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
    self.total_picked_expected_points = 0
    self.total_points_diff = 0
    self.entry_picks = {
      "imported_entries" : [],
      "actual_results" : 0,
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
    return str(self.seed)+" "+str(self.name)+ " "+str(self.elo)

  def update_elo(self, team_two, winner):
    # update elo for future rounds based on game outcome. 
    # Not sure how to do this for now so no update to elo will occur
    pass

  def toJSON(self, expanded=True, empty=False, array=False):
    if expanded:
      export_data = {
          "name" : self.name,
        "seed" : self.seed,
        "region" : self.region,
        "elo" : self.elo,
        "picked_frequency" : self.picked_frequency,
        "wins" : self.wins,
        "expected_points" : self.expected_points,
        "picked_expected_points": self.picked_expected_points,
        "points_diff": self.points_diff,
        "total_expected_points" : self.total_expected_points,
        "total_picked_expected_points": self.total_picked_expected_points,
        "total_points_diff": self.total_points_diff,
      }
      if array:
        export_data = [export_data]
    else:
      if empty:
        export_data = {
        self.name : 1,
        }
      else:
        wins = {
          "1" : 5,
          "2" : 4,
          "3" : 3,
          "4" : 3,
          "5" : 2,
          "6" : 2,
          "7" : 2,
          "8" : 2,
          "9" : 1,
          "10" : 1,
          "11" : 1,
          "12" : 1,
          "13" : 1,
          "14" : 1,
          "15" : 1,
          "16" : 1,
        }
        export_data = {
          self.name : wins[self.seed],
        }
    return export_data


class Game:
  # placeholder base class used as anytree implementation requires
  pass

class NodeGame(Game, NodeMixin):
  def __init__(self, model, team_one=Team('tbd',0,'tbd',-1,-1), team_two=Team('tbd',0,'tbd',-1,-1), parent=None, winner=None, children=None, region=None, round_num=7):
    super(NodeGame, self).__init__()
    self.team_one = team_one
    self.team_two = team_two
    self.parent = parent
    self.model = model
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
    return exporter.export(self.root)

  def simulate_game(self):
    # simulate the outcome of the game using 538's ELO system 
    # (sans travel adjustment) as seen here 
    # https://fivethirtyeight.com/methodology/how-our-march-madness-predictions-work-2/

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
    self.update_wins(self.model, self.winner, self.round_num)

  def update_wins(self, bracket, winner, round_number):
    teams = bracket.all_teams[winner.region][winner.seed]
    if len(teams)==1:
      team = teams[0]
      # if there was no play in game, increment round one win total to keep it 
      # aligned
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
    # between two teams in a matchup, pick the team with more of the given 
    # criteria. Used to visualize results
    
    if criteria == "randomized":
      total_perc = float(self.team_one.picked_frequency[self.round_num].strip('%')) + float(self.team_two.picked_frequency[self.round_num].strip('%'))
      chance = random.random()
      comp_one = float(getattr(self.team_one, 'picked_frequency')[self.round_num].strip('%'))
      comp_two = float(getattr(self.team_two, 'picked_frequency')[self.round_num].strip('%'))
      if chance < comp_one / total_perc or (chance == comp_one / total_perc and random.random() < 0.5):
        self.update_bracket(self.team_one)
      else:
        self.update_bracket(self.team_two)
      pass
    else:
      if type(getattr(self.team_one, criteria)[self.round_num]) is str:
        comp_one = float(getattr(self.team_one, criteria)[self.round_num].strip('%'))
        comp_two = float(getattr(self.team_two, criteria)[self.round_num].strip('%'))
      else:
        comp_one = getattr(self.team_one, criteria)[self.round_num]
        comp_two = getattr(self.team_two, criteria)[self.round_num]
      if comp_one > comp_two:
        self.update_bracket(self.team_one)
      elif comp_one < comp_two:
        self.update_bracket(self.team_two)
      else:
        # If the criteria is exactly the same than just pick a random team.
        # Normally only happens when the criteria is so close to zero that it 
        # gets rounded (like a late-round matchup between big underdogs) 
        # So not too impactful overall
        if random.random() < 0.5:
          self.update_bracket(self.team_one)
        else:
          self.update_bracket(self.team_two)
    
# Object used for a given entry, whether that be filled out bracket or a 
# bracket using postprocessed data.  In hindsight would it have been better to
# have the real entries and simulated entries be subclasses of 
# a base Entry class? maybe.
class Entry:
  def __init__(self, model, method, source):
    self.model = model
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

  def __repr__(self):
    return "Entry Ind "+str(self.index)+" entryID "+str(self.entryID)

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
    team_data = r'../team_data/team_'+self.model.gender+str(self.model.year)+'.json'
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

# The simulation results class contains results for each simulation completed 
# as well as information pertaining to the winners and any special brackets 
# filled out.
class Simulation_results:
  def __init__(self, model, actual=False, index=-1):
    self.model = model
    self.simulation_index = index
    self.actual = actual
    self.winning_score = 0
    self.winning_index = []
    self.beaten_by = {
      "most_valuable_teams" : False,
      "most_popular_teams" : False,
      "chalk" : False
    }
    self.number_of_entries = len(self.model.entries["imported_entries"])
    self.import_scoring_list()

  def __str__(self):
    if self.actual:
      return "Actual results, winning score of "+str(self.winning_score)+" by bracket(s) "+" ".join(str(self.winning_index))
    else:
      return "Simulation #"+str(self.simulation_index)+", winning score of "+str(self.winning_score)+" by bracket(s) "+" ".join("{0}".format(n) for n in self.winning_index)

  def __repr__(self):
    if self.actual:
      return "Actual results, winning score of "+str(self.winning_score)+" by bracket(s) "+" ".join(self.winning_index)
    else:
      return "Sim #"+str(self.simulation_index)+", win score of "+str(self.winning_score)+" by bracket(s) "+" ".join("{0}".format(n) for n in self.winning_index)

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
    # Populate rank results
    array = entry_results
    rank_vector = [0 for i in range(len(array))]
    placing_vector = [0 for i in range(len(array))]
    tuple_array = [(array[i], i) for i in range(len(array))]
    tuple_array.sort(reverse=True)
    (rank, n, i) = (1, 1, 0)
    while i < len(array):
      j = i
      while j < len(array) - 1 and tuple_array[j][0] == tuple_array[j+1][0]:
        j += 1
      n = j - i + 1
      for j in range(n):
        shared_index = tuple_array[i+j][1]
        rank_vector[shared_index] = rank + (n - 1) * 0.5
        placing_vector[shared_index] = rank
      rank += n
      i += n
    
    # Populate special bracket scores
    if self.actual:
      most_valuable_team_score = self.model.special_entries["most_valuable_teams"].scores["actual_results"]
      most_popular_team_score = self.model.special_entries["most_popular_teams"].scores["actual_results"]
      chalk_score = self.model.special_entries["chalk"].scores["actual_results"]
    else:
      most_valuable_team_score = self.model.special_entries["most_valuable_teams"].scores["simulations"][self.simulation_index]
      most_popular_team_score = self.model.special_entries["most_popular_teams"].scores["simulations"][self.simulation_index]
      chalk_score = self.model.special_entries["chalk"].scores["simulations"][self.simulation_index]
    # populate special bracket rankings.  Ranking does not affect actual entry scores.  I.e.:
    # if The most valuable team bracket scores 1800 and the entry scores are as follows:
    # score rank
    # 1820  1
    # 1810  2
    # 1790  3
    # The most valuable team would be ranked third, but the actual rankings will not change.
    def find_special_rankings(score, placing=False):
      lower_bound = -1
      higher_bound = 10000
      lower_index = -1
      higher_index = -1
      i=0
      higher_doubles = 0
      for i in range(len(entry_results)):
        if entry_results[i] == score:
          if placing:
            return placing_vector[i]
          else:
            return rank_vector[i]
        elif entry_results[i] > score:
          if entry_results[i] < higher_bound:
            higher_bound = entry_results[i]
            higher_index = i
            higher_doubles = 0
          elif entry_results[i] == higher_bound:
            higher_doubles += 1
        elif entry_results[i] < score:
          if entry_results[i] > lower_bound:
            lower_bound = entry_results[i]
            lower_index = i
        else:
          print("error, score incorrect")
      if higher_index == -1:
        if placing:
          return 1
        else:
          return 1.0
      elif lower_index == -1:
        if placing:
          return len(entry_results) + 1
        else:
          return float(len(entry_results)) + 1.0
      else:
        if placing:
          return round(rank_vector[higher_index] + 0.5*higher_doubles)+1
        else:
          return rank_vector[higher_index] + 1.0 + 0.5*higher_doubles



    most_valuable_team_rank = find_special_rankings(most_valuable_team_score)
    most_popular_team_rank = find_special_rankings(most_popular_team_score)
    chalk_rank = find_special_rankings(chalk_score)
    most_valuable_team_placing = find_special_rankings(most_valuable_team_score, True)
    most_popular_team_placing = find_special_rankings(most_popular_team_score, True)
    chalk_placing = find_special_rankings(chalk_score, True)
    self.scoring_list = {
      "entries" : entry_results,
      "most_valuable_teams" : most_valuable_team_score,
      "most_popular_teams" : most_popular_team_score,
      "chalk" : chalk_score
    }

    self.ranking_list = {
      "entries" : rank_vector,
      "most_valuable_teams" : most_valuable_team_rank,
      "most_popular_teams" : most_popular_team_rank,
      "chalk" : chalk_rank
    }

    self.placing_list = {
      "entries" : placing_vector,
      "most_valuable_teams" : most_valuable_team_placing,
      "most_popular_teams" : most_popular_team_placing,
      "chalk" : chalk_placing
    }
    for criteria in self.beaten_by:
      if self.scoring_list[criteria] >= winning_score:
        self.beaten_by[criteria] = True
        self.model.simulations_won_by_special_entries[criteria] += 1
    self.winning_score = winning_score
    self.winning_index = winning_index
    if not self.actual:
      self.model.winning_scores_of_simulations.append(winning_score)
      if len(self.model.simulations_won_by_imported_entries) != len(self.model.entries["imported_entries"]):
        for j in range(0,len(self.model.entries["imported_entries"])):
          self.model.simulations_won_by_imported_entries.append(0)
      # for i in winning_index:
          print(team.name+", "+team.region+", "+team.seed+", "+str(team.total_expected_points)+", "+str(team.total_picked_expected_points)+", "+str(team.total_points_diff)+", "+str(team.wins))
      #   self.model.simulations_won_by_imported_entries[i] += 1


def main():
  print("test")
  model = Model(number_simulations=10000, scoring_sys="degen_bracket", gender="mens", year=2024)
  model.batch_simulate()
  model.create_json_files()
  model.update_entry_picks()
  model.initialize_special_entries()
  model.analyze_special_entries()
  # model.add_fake_entries()
  # model.add_bulk_entries_from_database(2)
  model.add_simulation_results_postprocessing()
  model.output_results()

  print("yes")
  model.raw_print()
  # print("Name, Region, Seed, Total Expected Points, Total Picked Expected Points, Points Differential (Positive = Underrated)")
  # for region in model.all_teams:
  #   for seed in model.all_teams[region]:
  #     for team in model.all_teams[region][seed]:
  #       print(team.name+", "+team.region+", "+team.seed+", "+str(team.total_expected_points)+", "+str(team.total_picked_expected_points)+", "+str(team.total_points_diff))

  pass

if __name__ == '__main__':
  main()