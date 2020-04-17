from model.model import *

# 1. Gather team data from 538 and ESPN
#   a. Run check_ff_data_exists() from who_picked_scrape.py in /web_scraper
#       Output should be <year>_<gender>_who_picked.csv 
#       and <year>_fivethirtyeight_ncaa_forecasts.csv in team_data folder

#   b. Run csv_combine(<year>) from team_csv_combine.py in /team_data
#       Output should be <year>_all_prepped_data.csv

# 2. Scrape high-level bracket data from ESPN
#   a. Run ds.TopLevelScrape().main(PROXY, <bracket>) from data_scrape_main.py in /web_scraper
#       You may need to fetch a group from ESPN following the same format as the example brackets given
#       Output should be resultsPgi<#>.json in <gender><year>/top-level_results/<bracket_name>
# 
#   b. Run ds.BracketScrape().pass_to_consolidated(PROXY, <bracket>) from  data_scrape_main.py in /web_scraper
#       Output should be <bracket_prefix>_consolidated.json in /bracket_results

# 3. Extract preliminary pick value data
#   a.  
#

