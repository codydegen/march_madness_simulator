import random
import math
import pandas as pd
from anytree import Node, RenderTree, NodeMixin, AsciiStyle
from anytree.exporter import DotExporter
import os
import copy
import time

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
    1 : 0,
    2 : 10,
    3 : 20,
    4 : 40,
    5 : 80,
    6 : 160,
    7 : 320,
  },

  "wins_only" : {
    1 : 0,
    2 : 1,
    3 : 1,
    4 : 1,
    5 : 1,
    6 : 1,
    7 : 1,
  },

  "degen_bracket" : {
    1 : 0,
    2 : 2,
    3 : 3,
    4 : 5,
    5 : 8,
    6 : 13,
    7 : 21,
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

class Bracket:
  def __init__(self, gender='mens', year=2019, number_simulations=1, scoring_system=scoring_systems["ESPN"]):
    self.gender = gender
    self.year = year 
    self.all_teams = {}
    self.start_bracket = None
    self.running_bracket = None
    self.game_pairing = 0
    self.number_simulations = number_simulations
    self.completed_simulations = 0
    self.scoring_system = scoring_system
    pass

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
    self.running_bracket=copy.deepcopy(self.start_bracket)
    pass

  def batch_simulate(self):
    for i in range(0, self.number_simulations-1):
      self.simulate_bracket()
      # self.update_winners()
      self.reset_bracket()
      
      self.completed_simulations += 1
      if self.completed_simulations%100 == 0:
        print("simulation number "+str(i+1)+" completed.")

  def calculate_expected_points(self):
    for region in self.all_teams:
      for seed in self.all_teams[region]:
        for team in self.all_teams[region][seed]:
          total_expected_points = 0
          for ep in team.expected_points:
            round_expected_points = float(team.wins[ep]) / float(self.number_simulations) * float(self.scoring_system[ep])
            team.expected_points[ep] = round_expected_points
            total_expected_points += round_expected_points
          team.total_expected_points = total_expected_points
          print(team.name+" expected points: "+str(team.total_expected_points))
    pass

  def output_most_valuable_team(self):
    self.calculate_expected_points()
    most_valuable_bracket = copy.deepcopy(self.start_bracket)
    self.output_most_valuable_teams_for_full_bracket(most_valuable_bracket)
    print(RenderTree(most_valuable_bracket, style=AsciiStyle()))

  def create_teams(self):
    path = "data/"+str(self.year)+"_all_prepped_data.csv"

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
      # picks = [df["R64_picked"][ind], df["R32_picked"][ind], df["S16_picked"][ind], df["E8_picked"][ind], df["F4_picked"][ind], df["NCG_picked"][ind]]
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
      if len(team_seed) > 2:
        team_seed = team_seed[0:2]
      team_region = df["team_region"][ind]
      team_rating = df["team_rating"][ind]
      team = Team(team_name, team_seed, team_region, team_rating, picks)
      if team_region not in self.all_teams:
        self.all_teams[team_region] = {}
      if team_seed not in self.all_teams[team_region]:
        self.all_teams[team_region][team_seed] = [team]
      else:
        self.all_teams[team_region][team_seed].append(team)
    pass
  
  def create_bracket(self):
    finals = NodeGame(region="Finals")
    for ff_pairings in final_four_pairings[self.gender][self.year]:
      finals.add_child(self.add_semis(ff_pairings))
    self.start_bracket = finals
    self.running_bracket = copy.deepcopy(self.start_bracket)
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
      team_one = self.all_teams[region][seed_one]
      team_two = self.all_teams[region][seed_two]
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

  def prep_data(self, path):
    # placeholder function for now
    
    return None
  
  def simulate_bracket(self):
    self.simulate_bracket_recursion(self.running_bracket)
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


# my intuition is that I should be able to to both this and the previous functions using callbacks I'm not familiar enough with Python to know how to. May come back to this
  def output_most_valuable_teams_for_full_bracket(self, bracket):
    self.most_valuable_teams_recursion(bracket)
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
    self.total_expected_points = 0
    pass

  def __str__(self):
    return str(self.seed)+" "+str(self.name)+ " "+str(self.elo)+" EP: "+str(self.total_expected_points)

  def __repr__(self):
    # return "Name: "+str(self.name)+"\nseed: "+str(self.seed)+"\nRegion: "+str(self.region)+"\nRating: "+str(self.elo)
    return str(self.seed)+" "+str(self.name)+ " "+str(self.elo)

  def update_elo(self, team_two, winner):
    # update elo for future rounds based on game outcome. not sure how to do this for now so no update to elo will occur
    pass


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

  def __str__(self):
    return "R"+str(self.round_num)+" in the "+str(self.region)+" Region between "+str(self.team_one)+" and "+str(self.team_two)+"."

  def __repr__(self):
    if self.winner:
      return "R"+str(self.round_num)+" in the "+str(self.region)+" w/ "+str(self.team_one)+" vs "+str(self.team_two)+".  Winner is "+str(self.winner)
    else:
      return "R"+str(self.round_num)+" in the "+str(self.region)+" w/ "+str(self.team_one)+" vs "+str(self.team_two)+"."

  def simulate_game(self):
    # simulate the outcome of the game using 538's ELO system ( sans travel adjustment)
    # as seen here https://fivethirtyeight.com/methodology/how-our-march-madness-predictions-work-2/

    # make sure the game doesn't already have a winner
    assert not self.winner, "game between "+str(self.team_one)+" and  "+str(self.team_two)+" already has been played."

    team_one_chance = 1.0/(1.0 + pow(10,(-(self.team_one.elo-self.team_two.elo))*30.464/400))
    # print(self.team_one.name+"'s chance of winning vs "+self.team_two.name+" = "+str(math.trunc(team_one_chance*100))+"%")
    if random.random() < team_one_chance:
      # team one wins
      self.winner = self.team_one
      self.team_one.update_elo(self.team_two, True)
      self.team_two.update_elo(self.team_one, False)
    else:
      # team two wins
      self.winner = self.team_two
      self.team_one.update_elo(self.team_two, False)
      self.team_two.update_elo(self.team_one, True)
    # pass
    self.update_bracket(self.winner)
    self.update_wins(bracket, self.winner, self.round_num)
    # self.winner.wins[self.round_num] += 1

  def update_wins(self, bracket, winner, round_number):
    #     for region in all_teams:
    #   for seed in region:
    #     for team in seed:
    # for game in self.running_bracket.descendants:
    #   winner = game.winner
    teams = bracket.all_teams[winner.region][winner.seed]
    if len(teams)==1:
      team = teams[0]
    else:
      if teams[0].name == winner.name:
        team = teams[0]
      else:
        team = teams[1]
    team.wins[round_number] += 1
    # bracket.
    pass

  def update_bracket(self, winning_team):
    # update bracket with results of game
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
    
t=time.time()
bracket = Bracket(number_simulations=1000, scoring_system=scoring_systems["ESPN"])
bracket.create_teams()
bracket.create_bracket()
bracket.batch_simulate()
t = time.time() - t
print(RenderTree(bracket.start_bracket, style=AsciiStyle()))
print(t)
print(RenderTree(bracket.running_bracket, style=AsciiStyle()))
bracket.output_most_valuable_team()

