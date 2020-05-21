# march_madness

## Intro
This is a program to simulate March Madness so high-value teams can be identified for the purposes of creating the optimal bracket.  Visualizations of the results for entries for the March Madness Simulations are shown. Depending on the size of the pool entered, you can see how successful different strategies are, for example, going for a high-variance strategy (i.e., pick an out-of-left-field winner, make some savvy underdog picks) or just playing it safe (pick a high seed to win, generally err on the side of less chaos).

Current build can be found [here](https://cd-march-madness.herokuapp.com/).

## Technologies
* Written in [Python](https://www.python.org/)
* [Sqlite](https://www.sqlite.org/index.html) for database storage
* [selenium](https://www.selenium.dev/), [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) for web scraping
* [pandas](https://pandas.pydata.org/) for data analysis
* [Dash](https://plotly.com/dash/), [plotly](https://plotly.com/) for data visualization
* [Heroku](https://www.heroku.com/) for hosting

## Getting started
* Find the deployed website at http://cd-march-madness.herokuapp.com/
* Or run locally by
  * install python3
  * pip install -r requirements.txt --user
  * python -m app
  * See further documentation on workflow [here](/workflow.md) 

## Methodology
TBD

## To-Do
* Immediate:
  * Update documentation
* Long-term:
  * Enhance algorithm to develop bracket
    * Utilize who picked data to identify under-picked teams (Compare expected points versus picked percentage)
    * Enhance model to update elo after early round wins
  * Make output more user-friendly
    * Allow live input of entry
    * Allow entry or group import
    * Retain selected brackets when running subgroup analysis
    * Allow hot swapping between model inputs (swap between men's and women's natively, scoring system, increase number simulations or entries)
  * Allow for algorithmic creation of dummy brackets using who picked data
  * Structural:
    * Implement unit testing
    * Host database off-site to allow for larger data sets