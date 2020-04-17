import web_scrape_to_json as ds

# http://free-proxy.cz/en/proxylist/country/US/http/ping/all
PROXY = "156.96.118.58:3128"
PROXY = "52.179.231.206:80"

tournamentChallenge_2019 = {
  "groupname": "Tournament Challenge",
  "savepath": "Tournament_challenge_2019",
  "webaddress": "http://fantasy.espn.com/tournament-challenge-bracket/2019/en/group?groupID=196060",
  "groupsize": "100,000+",
  "year": 2019,
  "prefix" : "tc",
  "gender" : "mens"
}

sportsCenter_2019 = {
  "groupname": "ESPN's SportsCenter",
  "savepath": "ESPN_sportscenter_2019",
  "webaddress": "http://fantasy.espn.com/tournament-challenge-bracket/2019/en/group?groupID=1041234",
  "groupsize": "1,000,000+",
  "year": 2019,
  "prefix" : "sc",
  "gender" : "mens"
}

highlyQuestionable_2019 = {
  "groupname": "Highly Questionable!",
  "savepath": "Highly_questionable_2019",
  "webaddress": "http://fantasy.espn.com/tournament-challenge-bracket/2019/en/group?groupID=2895266",
  "groupsize": "29,000+",
  "year": 2019,
  "prefix" : "hq",
  "gender" : "mens"
}

sheaSerrano_2019 = {
  "groupname": "Shea Serrano",
  "savepath": "shea_serrano_2019",
  "webaddress": "http://fantasy.espn.com/tournament-challenge-bracket-women/2019/en/group?groupID=37871",
  "groupsize": "14,000+",
  "year": 2019,
  "prefix" : "ss",
  "gender" : "womens"
}

breannaStewart_2019 = {
  "groupname": "Breanna Stewart",
  "savepath": "breanna_stewart_2019",
  "webaddress": "http://fantasy.espn.com/tournament-challenge-bracket-women/2019/en/group?groupID=29393",
  "groupsize": "7,000+",
  "year": 2019,
  "prefix" : "bs",
  "gender" : "womens"
}

wnbaStars_2019 = {
  "groupname": "WNBA Stars",
  "savepath": "wnba_stars_2019",
  "webaddress": "http://fantasy.espn.com/tournament-challenge-bracket-women/2019/en/group?groupID=30053",
  "groupsize": "7,000+",
  "year": 2019,
  "prefix" : "ws",
  "gender" : "womens"
}

# dst = ds.TopLevelScrape()
# dst.main(PROXY, sheaSerrano_2019)
# dst.main(PROXY, breannaStewart_2019)
# dst.main(PROXY, wnbaStars_2019)


b = ds.BracketScrape()
b.pass_to_consolidated(PROXY, sheaSerrano_2019)