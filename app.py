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
number_simulations = 10
m = model.Model(number_simulations=number_simulations, gender="mens", scoring_sys="degen_bracket")
m.batch_simulate()
print("sims done")
m.create_json_files()
m.update_entry_picks()
m.initialize_special_entries()
m.analyze_special_entries()
m.add_bulk_entries_from_database(15)
m.add_simulation_results_postprocessing()



all_results = m.output_results()
special_wins = m.get_special_wins()
special_results = all_results[-4:]
entry_results = all_results[:-4]
overall_winning_score = special_results[special_results['name']=='winning_score']
overall_winning_score = overall_winning_score['simulations']
overall_winning_score_values = overall_winning_score.values[0]
# b = df(data=special_results)
# overall_winning_score.sort()
chalk = special_results[special_results['name']=='chalk']
chalk = chalk['simulations']
chalk_values = chalk.values[0]
most_valuable = special_results[special_results['name']=='most_valuable_teams']
most_valuable = most_valuable['simulations']
most_valuable_values = most_valuable.values[0]
most_popular_values = special_results[special_results['name']=='most_popular_teams']['simulations'].values[0]
# help(ff.create_distplot)
hist_data = [overall_winning_score_values, chalk_values, most_valuable_values, most_popular_values]
group_labels = ['Winning Score', 'Chalk', 'Most Valuable', 'Most Popular']
figure3 = ff.create_distplot(hist_data, group_labels, show_rug=False, show_curve=True, bin_size=1, histnorm='probability')
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

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([

    # dcc.Graph(
    #     id='winning-score-graph',
    #     figure=figure
    # ),
    dcc.Graph(
        id='winning-score-graph',
        figure=figure3
    ),
    dcc.Graph(
        id='test-graph',
        figure=figure2
    ),
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



if __name__ == '__main__':
    # model.main()

    app.run_server(debug=True)
