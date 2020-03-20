import random
import math
import pandas as pd
from anytree import Node, RenderTree, NodeMixin, AsciiStyle
from anytree.exporter import DotExporter
import os

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

seed_pairings = [[1,16],
                 [8,9],
                 [5,12],
                 [4,13],
                 [6,11],
                 [3,14],
                 [7,10],
                 [2,15]]

class Bracket:
  def __init__(self, gender='mens', year=2019):
    self.gender = gender
    self.year = year 
    self.all_teams = {}
    self.start_bracket = None
    self.game_pairing = 0
    pass


  def create_teams(self):
    path = "data/"+str(self.year)+"_all_prepped_data.csv"

    if os.path.exists(path):
      print(" found data")
      
    else:
      print(" couldn't find data")
      a = prep_data(path)

    team_data = pd.read_csv(path)
    gender_specific = team_data[team_data.gender == self.gender]
    earliest_date = gender_specific.forecast_date[-1:].values[-1]
    df = gender_specific[gender_specific.forecast_date == earliest_date]
    for ind in df.index:
      picks = [df["R64_picked"][ind], df["R32_picked"][ind], df["S16_picked"][ind], df["E8_picked"][ind], df["F4_picked"][ind], df["NCG_picked"][ind]]
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
    
    
    return None
    pass

  
  def simulate_bracket(self):
    self.simulate_bracket_recursion(self.start_bracket)
    pass
  
  def simulate_bracket_recursion(self, node):
    # print( "quotes similar in brackets" )
    for child in node.children:
      if hasattr(child.team_one, 'name'):
        self.simulate_bracket_recursion(child)
      if hasattr(child.team_two, 'name'):
        self.simulate_bracket_recursion(child)
      # if child.team_one[0].name != "tbd" and child.team_two[0].name != "tbd":
      child.simulate_game()
    pass



class Team:
  def __init__(self, name, rank, region, elo, picked_frequency):
    self.name = name
    self.rank = rank
    self.region = region
    self.elo = elo
    self.picked_frequency = picked_frequency
    pass

  def __str__(self):
    # return "Name: "+str(self.name)+"\nRank: "+str(self.rank)+"\nRegion: "+str(self.region)+"\nRating: "+str(self.elo)
    return str(self.rank)+" "+str(self.name)+ " "+str(self.elo)

  def __repr__(self):
    # return "Name: "+str(self.name)+"\nRank: "+str(self.rank)+"\nRegion: "+str(self.region)+"\nRating: "+str(self.elo)
    return str(self.rank)+" "+str(self.name)+ " "+str(self.elo)

  def funcname(self, parameter_list):
    pass

  def update_elo(self, team_two, winner):
    # update elo for future rounds based on game outcome
    pass


class Game:
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
    # if winner:
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
    # ssimulate the outcome of the game using 538's ELO system ( sans travel adjustment)
    # as seen here https://fivethirtyeight.com/methodology/how-our-march-madness-predictions-work-2/
    team_one_chance = 1.0/(1.0 + pow(10,(-(self.team_one.elo-self.team_two.elo))*30.464/400))
    
    print(self.team_one.name+"'s chance of winning vs "+self.team_two.name+" = "+str(math.trunc(team_one_chance*100))+"%")
    if random.random() < team_one_chance:
      # team one wins
      self.winner = self.team_one
      self.team_one.update_elo(self.team_two, True)
      self.team_two.update_elo(self.team_one, False)
    else:
      self.winner = self.team_two
      self.team_one.update_elo(self.team_two, False)
      self.team_two.update_elo(self.team_one, True)
    pass
    self.update_bracket(self.winner)

  def update_bracket(self, winning_team):
    if self.parent:
      if self.parent.team_one.name == "tbd":
        self.parent.team_one = winning_team 
      else:
        self.parent.team_two = winning_team 
    # update bracket with results of game
    pass

  
  def add_child(self, child):
    if type(child) is list:
      for i in child:
        i.parent = self
    else:
      print('s')
      child.parent = self
    # if len(self.children) == 0:
    #   self.children = [child]
    # else:
    #   self.children = [self.children[0], child]
    pass
    
bracket = Bracket()
bracket.create_teams()
bracket.create_bracket()
# print(RenderTree(bracket.start_bracket).by_attr(NodeGame))
print(RenderTree(bracket.start_bracket, style=AsciiStyle()))
# DotExporter(bracket.start_bracket).to_picture('test.png')
bracket.simulate_bracket()
print(RenderTree(bracket.start_bracket, style=AsciiStyle()))

# a = NodeGame()
# b = NodeGame(parent=a)
# c = NodeGame(team_one="bob")
# c.parent = b

# print(c)


