# march_madness

## Intro
Something that has always interested me is how optimal decision-making for building a March madness bracket depends so heavily on pool size. The strategy to win something like ESPN's super contest that regularly features over a million entries is a lot different from just trying to win your small work pool of 20 people. With this project I was hoping to identify some strategies for those of us trying to get really good at beating a few friends rather than trying to win a pool of millions of people.  Obviously this would've been more relevant if we had a tournament with which to test these strategies, but sometimes a global pandemic gets in the way of your little side project. What can you do.

## Approach

To start, I feel like there are three key things that you need to know in order to fill out a good bracket.

* Knowing who the best teams are
Of course, seeds are the obvious answer here, but there are many different advanced analytics models that we can use to help us identify under and over seeded teams.  My favorite to use is the one put forward by [538](https://projects.fivethirtyeight.com/2020-march-madness-predictions/).

* Knowing about how well you have to do to win
  * do you need to take big swings or just do pretty well?  This helps decide whether you want to take a risk on the winter or just pick one of the top few teams and hope that you can ride out the rest with better early bracket picks.
  *
* Knowing who other people are picking
The purpose here is to leverage what we know about other people to pick some teams that may be undervalued by the general public and avoid teams that are overvalued. I used the ["Who picked Whom"](http://fantasy.espn.com/tournament-challenge-bracket/2019/en/whopickedwhom) data from ESPN but there are likely other sources that would work equally well. A few ways this plays out:
  * there's an 8-9 or 7-10 matchup that analytics say is going to be a coin toss, but the public is heavily favoring one side of it.  Picking the other side of that matchup is an easy way to carve out a small advantage.
  * You're in a pool with a lot of people who are fans of a specific team in the tournament. No matter how good or bad that team is, people are to be picking them to go much further than they should be.  You can exploit that by picking a relatively early exit for that team.

## Methodology

## Technologies
* Python

## To-Do
* knowing who the best teams are
  * enhance model to update elo after early round wins
* knowing how well you have to do to win
  * figure out distribution of points
    * cleanup JSON data
    * scrape individual brackets
    * write code to simulate small pool from larger data set
* knowing who other people are picking
  * compare expected points versus who picked percentage
  * estimate homer factor (long way away)