import model.model as model
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
from pandas import DataFrame as df

dfd = pd.read_csv('https://gist.githubusercontent.com/chriddyp/5d1ea79569ed194d432e56108a04d188/raw/a9f9e8076b837d541398e999dcbac2b2826a81f8/gdp-life-exp-2007.csv')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

m = model.Model(number_simulations=1000, gender="mens")
m.batch_simulate()
m.create_json_files()
m.update_entry_picks()
m.initialize_special_entries()
m.analyze_special_entries()
m.add_bulk_entries_from_database(15)
m.add_simulation_results_postprocessing()
a = m.output_results()
b = df(data=a)

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([

    dcc.Graph(
        id='winning-score-graph',
        figure={
            'data' : [
                dict(
                    x=b['winning_score'],
                    type='histogram'
                )
            ],
            'layout' : dict(
                xaxis={'title' : 'Winning Score'},
                yaxis={'title' : 'Cumulative'}
            )
        }
    ),
    dcc.Graph(
        id='test-graph',
        figure={
            'data' : [
                dict(
                    x=b['winning_score'],
                    y=b['most_valuable_score'],
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    },
                )
            ],
            'layout' : dict(
                xaxis={'title' : 'Winning score'},
                yaxis={'title' : 'Most valuable score'}
            )
        }
    )
])



if __name__ == '__main__':
    # model.main()

    app.run_server(debug=True)
