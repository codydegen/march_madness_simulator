import random
import math
import pandas as pd
from anytree import Node, RenderTree, NodeMixin
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

      # if team_seed not in teams[team.region]:
      # print(self.all_teams[-1])
    
    pass
  
  def create_bracket(self):
    finals = NodeGame()
    for ff_pairings in final_four_pairings[self.gender][self.year]:
      final_four = NodeGame(parent=finals)
      for region in ff_pairings:
        elite_eight = NodeGame(round_num=5, region=region)
        game_pairing = 0
        for i in range(0,1):
          sweet_sixteen = NodeGame(region=region, parent=elite_eight)
          for j in range(0,1):
            ro32 = NodeGame(region=region, parent=sweet_sixteen)
            for k in range(0,1):
              seed_one = str(seed_pairings[game_pairing][0])
              seed_two = str(seed_pairings[game_pairing][1])
              team_one = self.all_teams[region][seed_one]
              team_two = self.all_teams[region][seed_two]
              # check for play in game
              if len(team_two) == 2:
                play_in = NodeGame(region=region, team_one=team_two[0], team_two=team_two[1],round_num=1)
                ro64 = NodeGame(region=region, team_one=team_one, children=[play_in], parent=ro32)
              else:
                ro64 = NodeGame(region=region, parent=ro32, team_one=team_one, team_two=team_two)
              game_pairing += 1
        final_four.add_child(elite_eight)
      # finals.add_child(final_four)
    self.start_bracket = finals
    # create top of bracket

    pass
  
  def prep_data(self, path):
    
    
    return None
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
    return "Name: "+str(self.name)+"\nRank: "+str(self.rank)+"\nRegion: "+str(self.region)+"\nRating: "+str(self.elo)

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
    if winner:
      self.winner = winner
    if children:
      self.children = children
    if region:
      self.region = region

  def __str__(self):
    return "Round "+str(self.round)+" matchup in the "+str(self.region)+" Region between "+str(self.team_one)+" and "+str(self.team_two)+"."

  def __repr__(self):
    return "Round "+str(self.round)+" matchup in the "+str(self.region)+" Region between "+str(self.team_one)+" and "+str(self.team_two)+"."


  def simulate_game(self):
    # ssimulate the outcome of the game using 538's ELO system ( sans travel adjustment)
    # as seen here https://fivethirtyeight.com/methodology/how-our-march-madness-predictions-work-2/
    team_one_chance = 1.0/(1.0 + pow(10,(-(self.team_one.elo-self.team_two.elo))*30.464/400))
    
    print(self.team_one.name+"'s chance of winning = "+str(math.trunc(team_one_chance*100))+"%")
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
    if len(self.children) == 0:
      self.children = [child]
    else:
      self.children = [self.children[0], child]
    pass
    
# a = Team('a',1,'south',89,0.4)
# b = Team('b',2,'south',87,0.3)
# c = Team('c',3,'south',85,0.2)
# d = Team('d',4,'south',83,0.1)

# finals = NodeGame()
# sf1 = NodeGame(a,d,finals)
# sf2 = NodeGame(b,c,finals)

# sf1.simulate_game()
# sf2.simulate_game()
# finals.simulate_game()

# for pre, _, node in RenderTree(finals):
#   treestr = u"%s%s" % (pre, node.round)
#   print(treestr.ljust(8), node.team_one.name, node.team_two.name, node.winner.name)

bracket = Bracket()
bracket.create_teams()
bracket.create_bracket()
# print(bracket)
print(bracket.start_bracket.descendants)

# for pre, _, node in RenderTree(bracket.start_bracket):
#   treestr = u"%s%s" % (pre, node.round_num)
#   print(treestr.ljust(8), node.team_one.name, node.team_two.name)


