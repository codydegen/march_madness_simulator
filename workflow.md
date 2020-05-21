The general workflow if downloading yourself for a data set with no data is Below.  The use case for this would be updating this tool for a new year. For example, 2021.

1. Gather team data from 538 and ESPN 
   * Run `check_ff_data_exists()` from who_picked_scrape.py in /web_scraper 
     * Output should be *\<year>_\<gender>_who_picked.csv* and *\<year>_fivethirtyeight_ncaa_forecasts.csv* in team_data folder.
   * Run `csv_combine(<year>)` from team_csv_combine.py in /team_data. 
     * Output should be *\<year>_all_prepped_data.csv*

2. Scrape high-level bracket data from ESPN  
   * Run `ds.TopLevelScrape().main(PROXY, <bracket>)` from *data_scrape_main.py* in */web_scraper*  
     * You may need to fetch a group from ESPN following the same format as the example brackets given  
     * Output should be *resultsPgi<#>.json* in *\<gender>\<year>/top-level_results/\<bracket_name>*
   * `Run ds.BracketScrape().pass_to_consolidated(PROXY, <bracket>)` from  *data_scrape_main.py* in */web_scraper*
     * Output should be *\<bracket_prefix>_consolidated.json* in */bracket_results*


3. Extract preliminary pick value data
   * Run `model.batch_simulate()` after creating a model with a nominal number of simulations (100-10000 is fine)
   * `model.create_json_files()` Will create *chalk.json*, *empty.json*, *reverse_lookup.json*, *preliminary_results.json*. 
     * You must fill in the information missing (wins for play in teams that lost must be set to 0 in the chalk and empty files, Overall number one and two seeds in the chalk file Should be set to seven and six wins respectively. If you're doing a retrospective analysis and want to look at how things compared to the actual results, you need to fill out the actual.json file as well)
     * The *preliminary_results.json* file may have some issues if team abbreviations are inconsistent During bracket scraping.  For example, LSU/Louisiana State, Abilene Christian/ACU, etc.  You will need to duplicate dictionaries for each spelling to point to the right place.


4. Run analysis of model
   * Model should now be able to run and output results.  The workflow detailed in the main function in the *model.py* script will output a dataframe with simulation results for a number of randomly selected brackets as well as the entries developed based on just picking chalk teams, picking the most popular teams, and picking the teams with the most expected points. 
   * The number of Entries analyzed can be determined using the `model.add_bulk_entries_from_database(number_of_entries)` method.


5. Visualize data
   * Running *app.py* will run a local server visualizing the data in various ways.  
   * The data can also be found online at http://cd-march-madness.herokuapp.com/

