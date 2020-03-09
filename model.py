import random

class MasterBracket:
  def __init__(self, parameter_list):
    pass

  def simulate_game(self, game_id):
    # ssimulate the outcome of the game using 538's ELO system ( sans travel adjustment)
    # as seen here https://fivethirtyeight.com/methodology/how-our-march-madness-predictions-work-2/
    teams = self.get_teams_by_game_id(game_id)
    team_one = teams[0]
    team_two = teams[1]
    team_one_chance = 1.0/(1.0 + 10 ** (-(team_one.elo-team_two.elo))*30.464/400)
    if random.random() < team_one_chance:
      # team one wins
      team_one.update_elo(team_two, True)
      team_two.update_elo(team_one, False)
      self.update_bracket(game_id, team_one)
    else:
      team_one.update_elo(team_two, False)
      team_two.update_elo(team_one, True)
      self.update_bracket(game_id, team_two)
    pass

  def get_teams_by_game_id(self, game_id):
    # return teams playing in a game relative to its ID
    pass

  def update_bracket(self, game_id, winning_team):
    # update bracket with results of game
    pass

class Team:
  def __init__(self, rank, region, elo, picked_frequency):
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

class OtherBracket:
  def __init__(self, parameter_list):
    pass

  def funcname(self, parameter_list):
    pass

class Pool:
  def __init__(self, number_teams):
    self.number_teams = number_teams
    pass

  def funcname(self, parameter_list):
    pass