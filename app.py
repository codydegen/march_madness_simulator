import model.model as model
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import scipy
from pandas import DataFrame as df

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
number_simulations = 50
m = model.Model(number_simulations=number_simulations, gender="mens")
m.batch_simulate()
m.create_json_files()
m.update_entry_picks()
m.initialize_special_entries()
m.analyze_special_entries()
m.add_bulk_entries_from_database(20)
m.add_simulation_results_postprocessing()
a = m.output_results()
winning_score = a[a['name']=='winning_score']
winning_score = winning_score.values.flatten()[2:]
# b = df(data=a)
# winning_score.sort()
chalk = a[a['name']=='chalk']
chalk = chalk.values.flatten()[2:]
most_valuable = a[a['name']=='most_valuable_teams']
most_valuable = most_valuable.values.flatten()[2:]
# chalk.sort()

# fig = go.Figure(
#     data=[
#         go.Histogram(
#             x=b["winning_score"],
#             cumulative_enabled=True,
#             visible=True,

#         )
#     ]
# )
figure2 = go.Figure(
    data=[
        go.Scatter(
            y=winning_score,
            x=np.linspace(0, number_simulations, number_simulations),
            name='Winning Score'
        )
    ]
)
figure2.add_trace(go.Scatter(
    y=chalk,
    x=np.linspace(0, number_simulations, number_simulations),
    name='Chalk'
))
figure2.add_trace(go.Scatter(
    y=most_valuable,
    x=np.linspace(0, number_simulations, number_simulations),
    name='Most Valuable Teams'
))
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([

    # dcc.Graph(
    #     id='winning-score-graph',
    #     figure=fig
    # ),
    dcc.Graph(
        id='test-graph',
        figure=figure2
    )
    # dcc.Graph(
    #     id='test-graph',
    #     figure={
    #         'data' : [
    #             dict(
    #                 x=b['winning_score'],
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
