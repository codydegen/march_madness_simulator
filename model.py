#! python3
import random
import math
import pandas as pd
from anytree import Node, RenderTree, NodeMixin, AsciiStyle
from anytree.exporter import DotExporter, JsonExporter
from anytree.importer import JsonImporter
import os
import copy
import time
import json
import queue


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

# different scoring systems for different brackets so expected points can be calculated
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
    self.simulation_results = []
    self.imported_brackets = []
    pass

  def create_teams(self):
    path = "data/"+str(self.year)+"_all_prepped_data.csv"
    all_teams = {}
    if os.path.exists(path):
      print(" found data")
      
    else:
      print(" couldn't find data")
      # TBD, hook up data scraping to this
      a = self.prep_data(path)

    team_data = pd.read_csv(path)
    gender_specific = team_data[team_data.gender == self.gender]
    earliest_date = gender_specific.forecast_date[-1:].values[-1]
    # data subset is the teams from the earliest date shown. This is the data from all of the teams are still in the tournament
    df = gender_specific[gender_specific.forecast_date == earliest_date]
    for ind in df.index:
      picks = {
        2:df["R64_picked"][ind], 
        3:df["R32_picked"][ind], 
        4:df["S16_picked"][ind], 
        5:df["E8_picked"][ind], 
        6:df["F4_picked"][ind], 
        7:df["NCG_picked"][ind], 
      }
      team_name = df["team_name"][ind]
      team_seed = df["team_seed"][ind]
      # team seeds in the imported file have an a or B suffix for playin games, this strips that 
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
    # self.sim_bracket.bracket=copy.deepcopy(self.start_bracket.bracket)
    self.sim_bracket.reset_bracket()
    pass

# simulation methods
  def batch_simulate(self):
    for i in range(0, self.number_simulations):
      # t = time.time()
      self.sim_bracket.simulate_bracket()
      self.update_scores()
      # a = time.time() - t
      # self.update_winners()
      self.reset_bracket()
      # b = time.time() - t
      # c = b-a
      self.completed_simulations += 1
      # if self.completed_simulations%100 == 0:
      # print("simulation number "+str(i)+" completed.")
      # print(a, c)
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

  def output_most_valuable_team(self):
    self.calculate_expected_points()
    most_valuable_bracket = Bracket(self)
    self.output_most_valuable_teams_for_full_bracket(most_valuable_bracket)
    return most_valuable_bracket

  def prep_data(self, path):
    # placeholder function for now
    
    return None
  
  # my intuition is that I should be able to to both this and the other recursive bracket manipulation functions using callbacks I'm not familiar enough with Python to know how to. May come back to this
  def output_most_valuable_teams_for_full_bracket(self, bracket):
    self.most_valuable_teams_recursion(bracket.bracket)
    # bracket.bracket.root.pick_more_valuable_team()
    pass
  
  def most_valuable_teams_recursion(self, node):
    # sorted DFS post order
    for child in node.children:
      # go through until there are no children
      if not hasattr(child.winner, 'name'):
        self.most_valuable_teams_recursion(child)
    # then sim game
    node.pick_more_valuable_team()
    pass

  def export_teams_to_json(self):
    return json.dumps(self.all_teams, default=lambda o: o.toJSON(), sort_keys=True, ensure_ascii=False)

  def add_entry(self, entry):
    entry.index = len(self.imported_brackets)
    self.imported_brackets.append(entry)
    self.update_entry_score(entry)

  def update_entry_score(self, entry):
    for region in self.all_teams:
      for seed in self.all_teams[region]:
        for team in self.all_teams[region][seed]:
          while len(team.entry_picks) < entry.index+1:
            team.entry_picks.append(-1)
          team.entry_picks[entry.index] = entry.team_picks[team.region][team.seed][team.name]
          for i in range(0, len(team.simulation_results)):
            if len(entry.scores) <= i:
              entry.scores.append(0)
            entry.scores[i] += self.scoring_system["cumulative"][min(team.simulation_results[i], team.entry_picks[entry.index])]
    pass

class Bracket:
  def __init__(self, model, method="empty", source=None):
    self.game_pairing = 0
    self.model = model
    if method == "empty":
      self.bracket = self.create_bracket()
    elif method == "json":
      self.bracket = self.import_bracket_json(source)
    elif method == "url":
      self.bracket = self.import_bracket_url(source)
    else:
      raise Exception("unknown method designated for bracket creation, creating empty bracket")
      self.bracket = create_bracket()
    pass

  def create_bracket(self):
    finals = NodeGame(region="Finals")
    for ff_pairings in final_four_pairings[self.model.gender][self.model.year]:
      finals.add_child(self.add_semis(ff_pairings))
    return finals
    pass
    
  
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
    # as it turns out is much more performant to just reset all the teams to blank rather than copying entire object
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
    results["method"] = "simulation"
    results["entryID"] = None
    results["source"] = None
    a = json.dumps(results)
    return a
    

    exporter = JsonExporter(sort_keys=True, default=lambda o: o.toJSON())
    c = str(exporter.export(bracket))
    # return exporter.export(self.root)
    return c

  def import_bracket_json(self, source):
    importer = JsonImporter()
    root = importer.import_(source) 
    c = json.loads(source)
    # root2 = importer.import_(d)
    return root
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
    self.entry_picks = []
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
    # return json.dumps(export_data)


class Game:
  # placeholder base class used as anytree implementation requires
  pass

class NodeGame(Game, NodeMixin):
  def __init__(self, team_one=Team('tbd',0,'tbd',-1,-1), team_two=Team('tbd',0,'tbd',-1,-1), parent=None, winner=None, children=None, region=None, round_num=7):
    super(NodeGame, self).__init__()
    self.team_one = team_one
    self.team_two = team_two
    self.parent = parent
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
    c = exporter.export(self.root)
    return exporter.export(self.root)

  def simulate_game(self):
    # simulate the outcome of the game using 538's ELO system ( sans travel adjustment)
    # as seen here https://fivethirtyeight.com/methodology/how-our-march-madness-predictions-work-2/

    # make sure the game doesn't already have a winner
    assert not self.winner, "game between "+str(self.team_one)+" and  "+str(self.team_two)+" already has been played."

    team_one_chance = 1.0/(1.0 + pow(10,(-(self.team_one.elo-self.team_two.elo))*30.464/400))
    # print(self.team_one.name+"'s chance of winning vs "+self.team_two.name+" = "+str(math.trunc(team_one_chance*100))+"%")
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
    # self.winner.wins[self.round_num] += 1

  def update_wins(self, bracket, winner, round_number):
    teams = bracket.all_teams[winner.region][winner.seed]
    if len(teams)==1:
      team = teams[0]
      # if there was no play in game, increment round one win total to keep it aligned
      if round_number == 2:
        team.wins[1] += 1
    else:
      if teams[0].name == winner.name:
        team = teams[0]
      else:
        team = teams[1]
    team.wins[round_number] += 1
    team.temp_result = round_number
    # if len(team.simulation_results) == bracket.completed_simulations:
    #   team.simulation_results.append(round_number)
    # elif len(team.simulation_results) < bracket.completed_simulations:
    #   while len(team.simulation_results) < bracket.completed_simulations:
    #     team.simulation_results.append(0)
    #   team.simulation_results.append(round_number)
    # else:
    #   team.simulation_results[bracket.completed_simulations] = round_number
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

  def pick_more_valuable_team(self):
    # between two teams in a matchup, pick the team with more expected points. Used to visualize results
    # self.team_one.total_expected_points = bracket.team_look_up(self.team_one).total_expected_points
    # self.team_two.total_expected_points = bracket.team_look_up(self.team_two).total_expected_points
    if self.team_one.total_expected_points > self.team_two.total_expected_points:
      self.update_bracket(self.team_one)
    elif self.team_one.total_expected_points < self.team_two.total_expected_points:
      self.update_bracket(self.team_two)
    else:
      print("Teams "+self.team_one.name+" and "+self.team_two.name+" have the same expected points.")
      if random.random() < 0.5:
        self.update_bracket(self.team_one)
      else:
        self.update_bracket(self.team_two)
    
class Entry:
  def __init__(self, method, source):
    if method == "empty":
      raise Exception("unknown method designated for bracket creation")
    elif method == "simulation":
      self.import_bracket_json(source)
    elif method == "url":
      self.bracket = self.import_bracket_url(source)
    else:
      raise Exception("unknown method designated for bracket creation")
      self.bracket = create_bracket()
    
    self.index = 0
    self.scores = []
    model.add_entry(self)

  def import_bracket_json(self, source):
    b = json.loads(source)
    self.team_picks = b["team_picks"]
    self.entryID = b["entryID"]
    self.method = b["method"]
    self.team_picks = b["team_picks"]
    self.source = b["source"]
    pass



t=time.time()
model = Model(number_simulations=1000, scoring_system=scoring_systems["ESPN"])
model.batch_simulate()
t = time.time() - t
print(t)
print(RenderTree(model.start_bracket.bracket, style=AsciiStyle()))
print(RenderTree(model.sim_bracket.bracket, style=AsciiStyle()))
a = model.output_most_valuable_team()
b = model.export_teams_to_json()
c = model.sim_bracket.export_bracket_to_json(a.bracket.root, "most valuable bracket")
d = Entry(method="simulation", source=c)
print(d)
