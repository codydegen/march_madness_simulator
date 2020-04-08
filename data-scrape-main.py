import ds

# http://free-proxy.cz/en/proxylist/country/US/http/ping/all
PROXY = "156.96.118.58:3128"
PROXY = "52.179.231.206:80"

tournamentChallenge_2019 = {
  "groupname": "Tournament Challenge",
  "savepath": "Tournament_challenge_2019",
  "webaddress": "http://fantasy.espn.com/tournament-challenge-bracket/2019/en/group?groupID=196060",
  "groupsize": "100,000+",
  "year": 2019
}

sportsCenter_2019 = {
  "groupname": "ESPN's SportsCenter",
  "savepath": "ESPN_sportscenter_2019",
  "webaddress": "http://fantasy.espn.com/tournament-challenge-bracket/2019/en/group?groupID=1041234",
  "groupsize": "1,000,000+",
  "year": 2019
}

highlyQuestionable_2019 = {
  "groupname": "Highly Questionable!",
  "savepath": "Highly_questionable_2019",
  "webaddress": "http://fantasy.espn.com/tournament-challenge-bracket/2019/en/group?groupID=2895266",
  "groupsize": "29,000+",
  "year": 2019
}

# dst = ds.TopLevelScrape()
# dst.main(PROXY, sportsCenter_2019)

b = ds.BracketScrape()
b.pass_to_consolidated(PROXY, highlyQuestionable_2019)