import random
import math
import pandas as pd
from anytree import Node, RenderTree, NodeMixin

class Bracket:
  def __init__(self, gender='men', year=2019):
    self.gender = gender
    pass

  # def simulate_game(self, game_id):
  #   # ssimulate the outcome of the game using 538's ELO system ( sans travel adjustment)
  #   # as seen here https://fivethirtyeight.com/methodology/how-our-march-madness-predictions-work-2/
  #   teams = self.get_teams_by_game_id(game_id)
  #   team_one = teams[0]
  #   team_two = teams[1]
  #   team_one_chance = 1.0/(1.0 + 10 ** (-(team_one.elo-team_two.elo))*30.464/400)
  #   if random.random() < team_one_chance:
  #     # team one wins
  #     team_one.update_elo(team_two, True)
  #     team_two.update_elo(team_one, False)
  #     self.update_bracket(game_id, team_one)
  #   else:
  #     team_one.update_elo(team_two, False)
  #     team_two.update_elo(team_one, True)
  #     self.update_bracket(game_id, team_two)
  #   pass

  # def get_teams_by_game_id(self, game_id):
  #   # return teams playing in a game relative to its ID
  #   pass



class Team:
  def __init__(self, name, rank, region, elo, picked_frequency):
    self.name = name
    self.rank = rank
    self.region = region
    self.elo = elo
    self.picked_frequency = picked_frequency
    pass

  def funcname(self, parameter_list):
    pass

  def update_elo(self, team_two, winner):
    # update elo for future rounds based on game outcome
    pass


class Game:
  pass

class NodeGame(Game, NodeMixin):
  def __init__(self, team_one=Team('tbd',0,'tbd',-1,-1), team_two=Team('tbd',0,'tbd',-1,-1), parent=None, winner=None, children=None):
    super(NodeGame, self).__init__()
    self.team_one = team_one
    self.team_two = team_two
    self.parent = parent
    if parent:
      self.round = parent.round - 1
    else:
      self.round = 6
    if winner:
      self.winner = winner
    if children:
      self.children = children

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
    
a = Team('a',1,'south',89,0.4)
b = Team('b',2,'south',87,0.3)
c = Team('c',3,'south',85,0.2)
d = Team('d',4,'south',83,0.1)

finals = NodeGame()
sf1 = NodeGame(a,d,finals)
sf2 = NodeGame(b,c,finals)

sf1.simulate_game()
sf2.simulate_game()
finals.simulate_game()

for pre, _, node in RenderTree(finals):
  treestr = u"%s%s" % (pre, node.round)
  print(treestr.ljust(8), node.team_one.name, node.team_two.name, node.winner.name)
# class OtherBracket:
#   def __init__(self, parameter_list):
#     pass

#   def funcname(self, parameter_list):
#     pass

# class Pool:
#   def __init__(self, number_teams):
#     self.number_teams = number_teams
#     pass

#   def funcname(self, parameter_list):
#     pass

# bob = Node("bob")
# joe = Node("joe", parent=bob)
# tim = Node("tim", parent=bob)
# jon = Node("jon", parent=tim)
# print(joe)

# for pre, fill, node in RenderTree(bob):
#   print("%s%s" % (pre, node.name))


