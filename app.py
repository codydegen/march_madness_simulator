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
    # figure = go.Figure(
    #     data=[
    #         go.Histogram(
    #             x=most_valuable_rank,
    #             name='Most Valuable'
    #         )
    #     ]
    # )
    # figure.add_trace(go.Histogram(
    #     x=chalk_rank,
    #     name='Chalk'
    # ))
    # # figure.add_trace(go.Histogram(
    # #     x=most_valuable_values,
    # #     name='Most Valuable Teams'
    # # ))
    # figure.add_trace(go.Histogram(
    #     x=most_popular_rank,
    #     name='Most Popular Teams'
    # ))
    # figure.update_layout(barmode='overlay')
    # figure.update_traces(opacity=0.5)
    return figure

def prepare_scores_graph(results):
    overall_winning_score_values = get_array_from_dataframe(all_results, 'simulations', 'winning_score')
    chalk_values = get_array_from_dataframe(results, 'simulations', 'chalk')
    most_valuable_values = get_array_from_dataframe(results, 'simulations', 'most_valuable_teams')
    most_popular_values = get_array_from_dataframe(results, 'simulations', 'most_popular_teams')
    hist_data = [overall_winning_score_values, chalk_values, most_valuable_values, most_popular_values]
    group_labels = ['Winning Score', 'Chalk', 'Most Valuable', 'Most Popular']
    return ff.create_distplot(hist_data, group_labels, show_rug=False, 
                                show_curve=True, bin_size=10, 
                                histnorm='probability')


if __name__ == '__main__':
    # model.main()
    number_simulations = 1000
    m = model.Model(number_simulations=number_simulations, gender="mens", scoring_sys="ESPN")
    m.batch_simulate()
    print("sims done")
    m.create_json_files()
    m.update_entry_picks()
    m.initialize_special_entries()
    m.analyze_special_entries()
    m.add_bulk_entries_from_database(30)
    m.add_simulation_results_postprocessing()



    all_results = m.output_results()
    special_wins = m.get_special_wins()
    special_results = all_results[-4:]
    entry_results = all_results[:-4]
    # 
    
    rank_figure=prepare_ranks_graph(all_results)
    score_figure = prepare_scores_graph(all_results)
    app.layout = html.Div([

        dcc.Graph(
            id='winning-score-graph',
            figure=score_figure
        ),

        dcc.Graph(
            id='ranks-graph',
            figure=rank_figure
        )
        
    ])
    app.run_server(debug=True)
