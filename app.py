import model.model as model
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np
import pandas as pd
import scipy
import math
from pandas import DataFrame as df

def random_subsample(n):
    subsample = entry_results.sample(n)
    return subsample



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def get_array_from_dataframe(frame, array_type, data_type):
    return frame[frame['name']==data_type][array_type].values[0]

def prepare_ranks_graph(results):
    most_valuable_rank = get_array_from_dataframe(results, 'ranks', 'most_valuable_teams')
    most_popular_rank = get_array_from_dataframe(results, 'ranks', 'most_popular_teams')
    chalk_rank = get_array_from_dataframe(results, 'ranks', 'chalk')

    hist_data = [most_valuable_rank, most_popular_rank, chalk_rank]
    group_labels = ['Most Valuable Teams', 'Most Popular Teams', 'Chalk']
    figure = ff.create_distplot(hist_data, group_labels, show_rug=True, 
                                show_curve=True, show_hist=True, bin_size=1, 
                                histnorm='probability')
    graph = dcc.Graph(
        id='ranking-graph',
        figure=figure
    )
    return graph

def prepare_scores_graph(results):
    overall_winning_score_values = get_array_from_dataframe(all_results, 'simulations', 'winning_score')
    chalk_values = get_array_from_dataframe(results, 'simulations', 'chalk')
    most_valuable_values = get_array_from_dataframe(results, 'simulations', 'most_valuable_teams')
    most_popular_values = get_array_from_dataframe(results, 'simulations', 'most_popular_teams')

    hist_data = [overall_winning_score_values, chalk_values, most_valuable_values, most_popular_values]
    group_labels = ['Winning Score', 'Chalk', 'Most Valuable', 'Most Popular']
    figure = ff.create_distplot(hist_data, group_labels, show_rug=False, 
                                show_curve=True, bin_size=10, 
                                histnorm='probability')
    graph = dcc.Graph(
        id='winning-score-graph',
        figure=figure
    )
    return graph

def prepare_table(results):

    def get_placings(place, inclusive=False, percentile=False, average=False):

        def get_sub_placings(data_set, place, inclusive, percentile, average):
            i=0
            if average:
                return round(np.average(data_set),1)
            if percentile:
                place = math.ceil(place/100*(len(results)-4))
            
            for score in data_set:
                if score>place:
                    break
                if percentile and score<=place:
                    i+=1
                elif inclusive and score<=place:
                    i+=1
                elif score==place:
                    i+=1
            return i
            

        score_array = []
        score_array.append(get_sub_placings(most_valuable_rank, place, inclusive, percentile, average))
        score_array.append(get_sub_placings(most_popular_rank, place, inclusive, percentile, average))
        score_array.append(get_sub_placings(chalk_rank, place, inclusive, percentile, average))
        return score_array

    most_valuable_rank = get_array_from_dataframe(results, 'placings', 'most_valuable_teams')
    most_valuable_rank.sort()
    most_popular_rank = get_array_from_dataframe(results, 'placings', 'most_popular_teams')
    most_popular_rank.sort()
    chalk_rank = get_array_from_dataframe(results, 'placings', 'chalk')
    chalk_rank.sort()
    data = {
        'Bracket Type' : {
            'Most Valuable Teams': [],
            'Most Popular Teams': [],
            'Chalk': [],
        }
    }
    columns = dict(values=['Bracket Type', '1st Places', '2nd Places', '3rd Places', 'Top 5', 'Top 10', 'Top 5%', 'Average Placing'],
                    align=['center','center'],
                    )
    bracket_type = ['Most Valuable Teams', 'Most Popular Teams', 'Chalk']
    first_places = get_placings(1)
    second_places = get_placings(2)
    third_places = get_placings(3)
    top_fives = get_placings(5,inclusive=True)
    top_tens = get_placings(10,inclusive=True)
    top_five_percentile = get_placings(5, percentile=True)
    average = get_placings(0, average=True)
    cells = dict(values=[bracket_type, first_places, second_places, third_places, top_fives, top_tens, top_five_percentile, average],
                align=['center','center'],
                height=30,)
    # figure_data = df.from_dict(data, orient='index', columns=columns)

    figure = go.Figure(data=[go.Table(header=columns, 
                                    cells=cells,
                                    columnwidth=[80,40,40,40,40,40,40,40])])
    graph = dcc.Graph(
        id='scoring-table',
        figure=figure
    )
    return graph


if __name__ == '__main__':
    # model.main()
    number_simulations = 200
    m = model.Model(number_simulations=number_simulations, gender="mens", scoring_sys="ESPN")
    m.batch_simulate()
    print("sims done")
    m.create_json_files()
    m.update_entry_picks()
    m.initialize_special_entries()
    m.analyze_special_entries()
    m.add_bulk_entries_from_database(17)
    m.add_simulation_results_postprocessing()



    all_results = m.output_results()
    special_wins = m.get_special_wins()
    special_results = all_results[-4:]
    entry_results = all_results[:-4]

    figures = []
    figures.append(prepare_ranks_graph(all_results))
    figures.append(prepare_table(all_results))
    figures.append(prepare_scores_graph(all_results))
    app.layout = html.Div(figures)
    app.run_server(debug=True)
