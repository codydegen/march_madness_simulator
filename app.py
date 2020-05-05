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
        show_curve=True, show_hist=True, bin_size=1, histnorm='probability')
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
    m.add_bulk_entries_from_database(100)
    m.add_simulation_results_postprocessing()



    all_results = m.output_results()
    special_wins = m.get_special_wins()
    special_results = all_results[-4:]
    entry_results = all_results[:-4]
    # overall_winning_score = special_results[special_results['name']=='winning_score']
    # overall_winning_score = overall_winning_score['simulations']
    overall_winning_score_values = get_array_from_dataframe(all_results, 'simulations', 'winning_score')
    # b = df(data=special_results)
    # overall_winning_score.sort()
    # chalk = special_results[special_results['name']=='chalk']
    # chalk = chalk['simulations']
    chalk_values = get_array_from_dataframe(all_results, 'simulations', 'chalk')
    # most_valuable = special_results[special_results['name']=='most_valuable_teams']
    # most_valuable = most_valuable['simulations']
    most_valuable_values = get_array_from_dataframe(all_results, 'simulations', 'most_valuable_teams')
    most_popular_values = get_array_from_dataframe(all_results, 'simulations', 'most_popular_teams')
    # help(ff.create_distplot)
    hist_data = [overall_winning_score_values, chalk_values, most_valuable_values, most_popular_values]
    group_labels = ['Winning Score', 'Chalk', 'Most Valuable', 'Most Popular']
    rank_figure=prepare_ranks_graph(all_results)

    figure3 = ff.create_distplot(hist_data, group_labels, show_rug=False, show_curve=True, bin_size=10, histnorm='probability')
    figure2 = go.Figure(
        data=[
            go.Scatter(
                y=overall_winning_score_values,
                x=np.linspace(0, number_simulations, number_simulations),
                name='Winning Score'
            )
        ]
    )
    figure2.add_trace(go.Scatter(
        y=chalk_values,
        x=np.linspace(0, number_simulations, number_simulations),
        name='Chalk'
    ))
    figure2.add_trace(go.Scatter(
        y=most_valuable_values,
        x=np.linspace(0, number_simulations, number_simulations),
        name='Most Valuable Teams'
    ))
    figure2.add_trace(go.Scatter(
        y=most_popular_values,
        x=np.linspace(0, number_simulations, number_simulations),
        name='Most Popular Teams'
    ))

    figure = go.Figure(
        data=[
            go.Histogram(
                x=overall_winning_score_values,
                name='Winning Score'
            )
        ]
    )
    figure.add_trace(go.Histogram(
        x=chalk_values,
        name='Chalk'
    ))
    figure.add_trace(go.Histogram(
        x=most_valuable_values,
        name='Most Valuable Teams'
    ))
    figure.add_trace(go.Histogram(
        x=most_popular_values,
        name='Most Popular Teams'
    ))
    figure.update_layout(barmode='overlay')
    figure.update_traces(opacity=0.5)

    # table = go.Figure(data=[
    #     go.Table(
    #         header=special_wins.keys(),
    #         cells=special_wins.values(),
    #     )
    # ])
    app.layout = html.Div([

        # dcc.Graph(
        #     id='winning-score-graph',
        #     figure=figure
        # ),
        dcc.Graph(
            id='winning-score-graph',
            figure=figure3
        ),
        # dcc.Graph(
        #     id='test-graph',
        #     figure=figure2
        # ),
        dcc.Graph(
            id='ranks-graph',
            figure=rank_figure
        )
        # dcc.Graph(
        #     id='table', 
        #     figure=table
        # )
        # dcc.Graph(
        #     id='test-graph',
        #     figure={
        #         'data' : [
        #             dict(
        #                 x=b['overall_winning_score'],
        #                 y=b['most_valuable_score'],
        #                 mode='markers',
        #                 opacity=0.7,
        #                 marker={
        #                     'size': 15,
        #                     'line': {'width': 0.5, 'color': 'white'}
        #                 },
        #             )
        #         ],
        #         'layout' : dict(
        #             xaxis={'title' : 'Winning score'},
        #             yaxis={'title' : 'Most valuable score'}
        #         )
        #     }
        # )
    ])
    app.run_server(debug=True)
