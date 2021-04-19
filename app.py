import model.model as model
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np
import pandas as pd
import scipy
import math
import dash_table as dt
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Sign
from pandas import DataFrame as df
from collections import OrderedDict
from plotly.colors import n_colors
import os
import json

######################### CHANGE THESE PARAMETERS #############################
number_simulations = 500
real_entries = 10
fake_entries = 50
number_entries = real_entries + fake_entries
year = 2021
gender = "mens"
# Scoring systems currently implemented are "ESPN", "wins_only", "degen_bracket"
scoring_system = "ESPN"

external_stylesheets = ['../assets/styles.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title='March Madness Simulator'

# Helper function
# TODO There may be a more effective way of doing this in pandas 
def get_array_from_dataframe(frame, array_type, data_type):
    return frame[frame['name']==data_type][array_type].values[0]

def count_occurrences(data):
    dictionary = {}
    increment = 1/len(data)
    for i in data:
        if not dictionary.get(i):
            dictionary[i] = 0
        dictionary[i] += increment
    ordered = OrderedDict(sorted(dictionary.items()))
    return ordered

# Ranks graph function
def prepare_ranks_graph(results):
    group_labels = [result for result in results['name']]
    array_results = [get_array_from_dataframe(results, 'ranks', result) for result in group_labels]
    try:
        figure = ff.create_distplot(array_results, group_labels, show_rug=False, 
                                    show_curve=False, show_hist=True, bin_size=1, 
                                    histnorm='probability')
    except:
        print('Singular matrix error')
        raise PreventUpdate
        # figure = ff.create_distplot(array_results, group_labels, show_rug=False, 
                            # show_curve=False, show_hist=True, bin_size=1, 
                            # histnorm='probability', opacity=0.5)
    figure.update_layout(
        title_text='Histogram of Final Placements',
        xaxis_title='Placing',
        yaxis_title='Share of Simulations'
    )
    return figure

# Scores graph function
def prepare_scores_graph(results):
    # overall_winning_score_values = get_array_from_dataframe(special_results, 'simulations', 'winning_score')
    group_labels = [result for result in results['name']]
    array_results = [get_array_from_dataframe(results, 'simulations', result) for result in group_labels]

    # hist_data = [overall_winning_score_values, chalk_values, most_valuable_values, most_popular_values]
    # group_labels = ['Winning Score', 'Chalk', 'Most Valuable', 'Most Popular']
 
    # figure = go.Figure()
    # converted_array_results = [count_occurrences(data) for data in array_results]
    # for i in range(len(converted_array_results)):
    #     figure.add_trace(go.Scatter(name=group_labels[i],x=list(converted_array_results[i].keys()),y=list(converted_array_results[i].values()))) 

    figure = ff.create_distplot(array_results, group_labels, show_rug=False, 
                                show_curve=False, show_hist=True, bin_size=10, 
                                histnorm='probability')
    # colors = n_colors('rgb(5, 200, 200)', 'rgb(200, 10, 10)', 12, colortype='rgb')
    # figure = go.Figure()
    
    # for array, label in zip(array_results, group_labels):
    #     figure.add_trace(go.Violin(y=array, box_visible=False, line_color='black',
    #                            meanline_visible=True,  opacity=0.6,
    #                            x0=label))

    # figure.update_layout(yaxis_zeroline=False)

    # for array, color, name in zip(array_results, colors, group_labels):
    #     figure.add_trace(go.Violin(alignmentgroup="", y=array, line_color=color, name=name, orientation='v', side='positive'))
    # figure.update_traces(orientation='v', side='positive', meanline_visible=True,
                #   points=False,
                #   jitter=1.00,
    # )
    # figure.update_traces(orientation='h', side='positive', width=3, points=False)
    # figure.update_layout(violinmode='overlay', violingroupgap=0, violingap=0)
    figure.update_layout(
        title_text='Histogram of Final Scores',
        xaxis_title='Score',
        yaxis_title='Share of Simulations'
    )
    return figure

# Table preparation function
def prepare_table(entry_results, special_results, sims):

    def get_sub_placings(data_set, place, inclusive=False, percentile=False, average=False):
        i=0
        if average:
            return round(np.average(data_set),1)
        if percentile:
            place = math.ceil(place/100*(len(entry_results)))
        
        for score in data_set:
            if score>place:
                break
            if percentile and score<=place:
                i+=1
            elif inclusive and score<=place:
                i+=1
            elif score==place:
                i+=1
        return round(i/sims, 3)

    def convert_entry_to_dictionary(dataframe, name):
        ranks = get_array_from_dataframe(dataframe, 'placings', name)
        ranks.sort()
        index = dataframe[dataframe['name'] == name]['entryID'].values[0]
        percentiles = [get_sub_placings(ranks, 25, percentile=True), 
                       get_sub_placings(ranks, 50, percentile=True), 
                       get_sub_placings(ranks, 75, percentile=True), 
                    #    get_sub_placings(ranks, 80, percentile=True), 
                       1]
        entry = {
            'Index': index,
            'Entry': name,
            '1st': get_sub_placings(ranks, 1),
            '2nd': get_sub_placings(ranks, 2),
            # '3rd': get_sub_placings(ranks, 3),
            # 'Top Five': get_sub_placings(ranks, 5, inclusive=True),
            # 'Top Ten': get_sub_placings(ranks, 10, inclusive=True),
            '1st Q.': percentiles[0],
            '2nd Q.': percentiles[1]-percentiles[0],
            '3rd Q.': percentiles[2]-percentiles[1],
            '4th Q.': percentiles[3]-percentiles[2],
            # '5th Q.': percentiles[4]-percentiles[3],
            'Avg Plc.': get_sub_placings(ranks, 0, average=True),
        }
        return entry
    # Get rankings and then sort them
    data_array = []
    data_array.append(convert_entry_to_dictionary(special_results, 'most_valuable_teams'))
    data_array.append(convert_entry_to_dictionary(special_results, 'most_popular_teams'))
    data_array.append(convert_entry_to_dictionary(special_results, 'chalk'))
    for entry in entry_results['name']:
        data_array.append(convert_entry_to_dictionary(entry_results, entry))

    print("updating table viz")
    return data_array

# As currently written, changing the maximum value here is okay. Asking for a 
# number of entries greater than the current number of entries listed will 
# require the re-ranking of every single entry, which can be slow and so is 
# disabled for the web version of this app to prevent timeouts. However, this 
# can be changed if you're running this locally.
def prepare_number_entries_input():
    entries_input = dcc.Input(
        id='number-entries-input',
        type='number',
        value=number_entries,
        max=number_entries,
        min=0
    )
    return entries_input 

# Unlike with the number of entries, the number of simulations cannot exceed 
# the original number simulations run. If you want to add simulations you will 
# need to restart from the very beginning with a greater number.
def prepare_number_simulations_input():
    simulations_input = dcc.Input(
        id='number-simulations-input',
        type='number',
        value=number_simulations,
        max=number_simulations,
        min=0
    )
    return simulations_input 

def prepare_run_button_input():
    button = html.Button(id='run-input', n_clicks=0, children='Run Subgroup Analysis')
    return button

# Callback to update once results change
@app.callback(
     [Output(component_id='scoring-table', component_property='data'),
     Output(component_id='scoring-table', component_property='selected_rows'),
     Output('hidden-dataframe', 'children')],
    [Input(component_id='run-input', component_property='n_clicks')],
    [State('number-entries-input', 'value'),
     State('number-simulations-input', 'value')])
def update_table(n_clicks, entry_input, simulations_input):
    global all_results
    current_number_of_entries = len(all_results['entryID'])-4
    if current_number_of_entries < entry_input:
        m.add_bulk_entries_from_database(entry_input-current_number_of_entries)
        m.add_simulation_results_postprocessing()
        all_results = m.output_results()
        special_wins = m.get_special_wins()
        special_results = all_results[-4:]
        entry_results = all_results[:-4]
    
    filtered_dataframe = m.analyze_sublist(all_results, entry_input, simulations_input)
    filtered_special_results = filtered_dataframe[-4:]
    filtered_entry_results = filtered_dataframe[:-4]
    scoring_table = prepare_table(filtered_entry_results, filtered_special_results, simulations_input)
    print("update complete")
    return scoring_table, [0, 1], filtered_dataframe.to_json(orient='split')

# Create each individual region
def create_region(region, stages, initial_game_number):
    stage_html_list=[]
    for stage in stages:
        game_html_list = []
        for i in range(stages[stage]):
            game_html_list.append(html.Div([
                html.Div('', id='game'+str(initial_game_number)+'-team1', className='team team1'),
                html.Div('', id='game'+str(initial_game_number)+'-team2', className='team team2'),
            ], id='game'+str(initial_game_number), className=region+' '+stage+' g'+str(i)+' game'))
            initial_game_number+=1
        stage_html_list.append(
            html.Div(game_html_list, className='inner-bounding '+stage))
    return html.Div(stage_html_list, className='region-container bounding-'+region)


# Create the outline of the bracket used for visualizations
def create_bracket():
# Dictionary of each of the stages associated with the given region and the 
# number of games per region for that stage
    stages = {
        'n64' : 8, 
        'n32' : 4,
        'n16' : 2,
        'n8' : 1
    }
    bounding_html_list = []
    left_region_html_list = []
    left_region_html_list.append(create_region('r1', stages, 0))
    left_region_html_list.append(create_region('r2', stages, 15))
    right_region_html_list = []
    right_region_html_list.append(create_region('r3', stages, 30))
    right_region_html_list.append(create_region('r4', stages, 45))
    bounding_html_list.append(
        html.Div(left_region_html_list, className='left-bounding')
    )
    bounding_html_list.append(
        html.Div([html.Div([
            html.Div('', id='game60-team1', className='team team1'),
            html.Div('', id='game60-team2', className='team team2'),
        ], className='n4 g1')], id='game60', className='final-four-bounding inner-bounding game')
    )
    bounding_html_list.append(
        html.Div([html.Div([
            html.Div('', id='game62-team1', className='team team1'),
            html.Div('', id='game62-team2', className='team team2'),
        ], className='n2 g1')], id='game62', className='finals-bounding inner-bounding game')
    )
    bounding_html_list.append(
        html.Div([html.Div([
            html.Div('', id='game61-team1', className='team team1'),
            html.Div('', id='game61-team2', className='team team2'),
        ], className='n4 g2')], id='game61', className='final-four-bounding inner-bounding game')
    )
    bounding_html_list.append(
        html.Div(right_region_html_list, className='right-bounding')
    )
    bracket_html = html.Div(bounding_html_list, className='bounding-bracket')
    return bracket_html


###############################################################################
################################ Global code ##################################
###############################################################################

m = model.Model(number_simulations=number_simulations, gender=gender, scoring_sys=scoring_system, year=year)
m.batch_simulate()
print("sims done")
m.create_json_files()
m.update_entry_picks()
m.initialize_special_entries()
m.analyze_special_entries()
m.add_fake_entries(fake_entries)
m.add_bulk_entries_from_database(real_entries)
m.add_simulation_results_postprocessing()
m.raw_print()
all_results = m.output_results()
all_results = m.output_results()
special_wins = m.get_special_wins()
special_results = all_results[-4:]
entry_results = all_results[:-4]
table_columns_pre=['Entry']
table_columns_places=['1st', '2nd'] 
table_columns_quintiles=['1st Q.', '2nd Q.', '3rd Q.', '4th Q.']
table_columns_post=['Avg Plc.']
###############################################################################
################################ Global code ##################################
###############################################################################
def discrete_background_color_bins(df, n_bins=9, columns='all', dark_color='Blues'):
    import colorlover
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    if columns == 'all':
        if 'id' in df:
            df_numeric_columns = df.select_dtypes('number').drop(['id'], axis=1)
        else:
            df_numeric_columns = df.select_dtypes('number')
    else:
        df_numeric_columns = df[columns]
    df_max = 1
    df_min = 0
    ranges = [
        ((df_max - df_min) * i) + df_min
        for i in bounds
    ]
    styles = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        backgroundColor = colorlover.scales[str(n_bins)]['seq'][dark_color][i - 1]
        color = 'white' if i > len(bounds) / 2. else 'inherit'

        for column in df_numeric_columns:
            styles.append({
                'if': {
                    'filter_query': (
                        '{{{column}}} >= {min_bound}' +
                        (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                    ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                    'column_id': column
                },
                'backgroundColor': backgroundColor,
                'color': color
            })
    return styles

table_data = prepare_table(entry_results, special_results, number_simulations)
figures = [
    html.Header(children=[
        html.Ul(children=[
            html.Li(children=
                html.A(href='https://github.com/codydegen/march_madness', children='GitHub')),
            html.Li(children=
                html.A(href='mailto:codydegen+dev@gmail.com', children='Contact Me')),
            ], id='header-list'
        )
    ]),
    html.H1('Simulation Of '+gender.capitalize()[:-1]+'\'s March Madness Brackets: '+str(year)),
    html.P(children=['A pool of '+str(number_entries)+' brackets is simulated '+
    str(number_simulations)+' times to see who has the best-performing brackets'+
    ' over time. Entries in ',html.Span('beige', id='beige'),' are '+
    'algorithmicly generated.  "most_valuable_teams" is generated using ',
    html.A(href='https://projects.fivethirtyeight.com/'+str(year)+
        '-march-madness-predictions/',children='538\'s Power Rating to estimate'+
        ' the best teams'),', "most_popular_teams" is generated using ',
    html.A(href='http://fantasy.espn.com/tournament-challenge-bracket/'+
        str(year)+'/en/whopickedwhom', children=' ESPN\'s most popular teams'),
    ' and "chalk" is generated by picking the highest seed in every matchup.  '+
    'Select entries in the table to visualize the picks, or see how they stack'+
    ' up by placement or by raw score.  If you\'d like to see the results for'+
    ' a small group of entries or simulations, scroll to the bottom and you '+
    'can see how things might change.  Check back (hopefully) in 2021 for help '+
    'building the ideal bracket for any pool size!']),
    dt.DataTable(
        id="scoring-table",
        columns=[{"name": i, "id": i} for i in table_columns_pre]+ 
                [{"name": i, "id": i, "type": "numeric", "format": FormatTemplate.percentage(1)} for i in table_columns_places] + 
                [{"name": i, "id": i, "type": "numeric", "format": FormatTemplate.percentage(1)} for i in table_columns_quintiles] +
                [{"name": i, "id": i} for i in table_columns_post],
        data=table_data,
        row_selectable='multi',
        fixed_rows={'headers': True},
        selected_rows=[0],
        sort_action='native',
        style_cell={'textAlign': 'left',
                    'width': '40px'},
        style_table={'height': '300px', 'overflowY': 'auto'},
        style_data_conditional=discrete_background_color_bins(df(data=table_data), columns=table_columns_quintiles)+
                                discrete_background_color_bins(df(data=table_data), columns=table_columns_places, dark_color='Greens')+
                                [{
                                    'if': {
                                        'filter_query': '{Index} < 0',  # matching rows of a hidden column with the id, `id`
                                        'column_id': 'Entry'
                                    },
                                    'backgroundColor': 'rgb(255,248,220)'
                                },
                                {
                                    'if': {'column_id': 'Entry'},
                                    'width': '120px'
                                },
                                {

                                }],
        ),
    html.Label([
        "Visualize a Bracket:",
        dcc.Dropdown(
            id='bracket-dropdown',
            options=[
                {'label': 'most_valuable_teams', 'value': -2},
            ],
            value=-2,
            # clearable=False
    ),]),
    create_bracket(), 
    dcc.Graph(
        id='ranking-graph',
        figure=prepare_ranks_graph(special_results[-3:-1])),
    dcc.Graph(
        id='winning-score-graph',
        figure=prepare_scores_graph(special_results[-3:-1])),
    html.H5('Run Subgroup Analysis', id='subgroup-analysis-label'),
    html.Div([
        html.Div([
            html.H6('Number Of Entries'),
            prepare_number_entries_input(),
            html.P('Maximum: '+str(number_entries)),
        ], className="entries-box"),
        html.Div([
            html.H6('Number Of Simulations'),
            prepare_number_simulations_input(),
            html.P('Maximum: '+str(number_simulations)),
        ], className="simulations-box"),
        ], id="subgroup-bounding-box"),
    html.Div([
        prepare_run_button_input(),
    ], id="run-button"),
    html.Div(id='hidden-dataframe', style={'display': 'none'}),
]

app.layout = html.Div(figures)

def create_output_list_for_bracket_callback():
    stages = {
        'n64' : 8, 
        'n32' : 4,
        'n16' : 2,
        'n8' : 1
    }
    output_list = []
    left_regions = m.bracket_pairings[0]
    right_regions = m.bracket_pairings[1]
    region_number=1

    def populate_sublist_region(output_list, regions, region_number):
        for i in range(63):
            output_list.append(Output(component_id='game'+str(i), component_property='children'))
            region_number+=1

    def populate_sublist_final_four(output_list):
        game_ids = ['n4-g0', 'n2-g0', 'n4-g1']
        for game_id in game_ids:
            output_list.append(Output(component_id=game_id+'-game', component_property='children'))

    populate_sublist_region(output_list, left_regions, 1)
    return output_list
# output_list = create_output_list_for_bracket_callback()

@app.callback(
    create_output_list_for_bracket_callback(), 
    [Input('bracket-dropdown', 'value')],
)
def fill_bracket_visualization(entryID):
    if entryID == None:
        print(' no entry ID provided')
        raise PreventUpdate
    team_ordering = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]
    new_team_paths = [
         [[0, 0], [8, 0],  [12, 0], [14, 0], [60, 0], [62, 0], [62, 0]],
         [[0, 1], [8, 0],  [12, 0], [14, 0], [60, 0], [62, 0], [62, 0]],
         [[1, 0], [8, 1],  [12, 0], [14, 0], [60, 0], [62, 0], [62, 0]],
         [[1, 1], [8, 1],  [12, 0], [14, 0], [60, 0], [62, 0], [62, 0]],
         [[2, 0], [9, 0],  [12, 1], [14, 0], [60, 0], [62, 0], [62, 0]],
         [[2, 1], [9, 0],  [12, 1], [14, 0], [60, 0], [62, 0], [62, 0]],
         [[3, 0], [9, 1],  [12, 1], [14, 0], [60, 0], [62, 0], [62, 0]],
         [[3, 1], [9, 1],  [12, 1], [14, 0], [60, 0], [62, 0], [62, 0]],
        [[4, 0],  [10, 0], [13, 0], [14, 1], [60, 0], [62, 0], [62, 0]],
        [[4, 1],  [10, 0], [13, 0], [14, 1], [60, 0], [62, 0], [62, 0]],
        [[5, 0],  [10, 1], [13, 0], [14, 1], [60, 0], [62, 0], [62, 0]],
        [[5, 1],  [10, 1], [13, 0], [14, 1], [60, 0], [62, 0], [62, 0]],
        [[6, 0],  [11, 0], [13, 1], [14, 1], [60, 0], [62, 0], [62, 0]],
        [[6, 1],  [11, 0], [13, 1], [14, 1], [60, 0], [62, 0], [62, 0]],
        [[7, 0],  [11, 1], [13, 1], [14, 1], [60, 0], [62, 0], [62, 0]],
        [[7, 1],  [11, 1], [13, 1], [14, 1], [60, 0], [62, 0], [62, 0]],
        [[15, 0], [23, 0], [27, 0], [29, 0], [60, 1], [62, 0], [62, 0]],
        [[15, 1], [23, 0], [27, 0], [29, 0], [60, 1], [62, 0], [62, 0]],
        [[16, 0], [23, 1], [27, 0], [29, 0], [60, 1], [62, 0], [62, 0]],
        [[16, 1], [23, 1], [27, 0], [29, 0], [60, 1], [62, 0], [62, 0]],
        [[17, 0], [24, 0], [27, 1], [29, 0], [60, 1], [62, 0], [62, 0]],
        [[17, 1], [24, 0], [27, 1], [29, 0], [60, 1], [62, 0], [62, 0]],
        [[18, 0], [24, 1], [27, 1], [29, 0], [60, 1], [62, 0], [62, 0]],
        [[18, 1], [24, 1], [27, 1], [29, 0], [60, 1], [62, 0], [62, 0]],
        [[19, 0], [25, 0], [28, 0], [29, 1], [60, 1], [62, 0], [62, 0]],
        [[19, 1], [25, 0], [28, 0], [29, 1], [60, 1], [62, 0], [62, 0]],
        [[20, 0], [25, 1], [28, 0], [29, 1], [60, 1], [62, 0], [62, 0]],
        [[20, 1], [25, 1], [28, 0], [29, 1], [60, 1], [62, 0], [62, 0]],
        [[21, 0], [26, 0], [28, 1], [29, 1], [60, 1], [62, 0], [62, 0]],
        [[21, 1], [26, 0], [28, 1], [29, 1], [60, 1], [62, 0], [62, 0]],
        [[22, 0], [26, 1], [28, 1], [29, 1], [60, 1], [62, 0], [62, 0]],
        [[22, 1], [26, 1], [28, 1], [29, 1], [60, 1], [62, 0], [62, 0]],        
        [[30, 0], [38, 0], [42, 0], [44, 0], [61, 0], [62, 1], [62, 1]],
        [[30, 1], [38, 0], [42, 0], [44, 0], [61, 0], [62, 1], [62, 1]],
        [[31, 0], [38, 1], [42, 0], [44, 0], [61, 0], [62, 1], [62, 1]],
        [[31, 1], [38, 1], [42, 0], [44, 0], [61, 0], [62, 1], [62, 1]],
        [[32, 0], [39, 0], [42, 1], [44, 0], [61, 0], [62, 1], [62, 1]],
        [[32, 1], [39, 0], [42, 1], [44, 0], [61, 0], [62, 1], [62, 1]],
        [[33, 0], [39, 1], [42, 1], [44, 0], [61, 0], [62, 1], [62, 1]],
        [[33, 1], [39, 1], [42, 1], [44, 0], [61, 0], [62, 1], [62, 1]],
        [[34, 0], [40, 0], [43, 0], [44, 1], [61, 0], [62, 1], [62, 1]],
        [[34, 1], [40, 0], [43, 0], [44, 1], [61, 0], [62, 1], [62, 1]],
        [[35, 0], [40, 1], [43, 0], [44, 1], [61, 0], [62, 1], [62, 1]],
        [[35, 1], [40, 1], [43, 0], [44, 1], [61, 0], [62, 1], [62, 1]],
        [[36, 0], [41, 0], [43, 1], [44, 1], [61, 0], [62, 1], [62, 1]],
        [[36, 1], [41, 0], [43, 1], [44, 1], [61, 0], [62, 1], [62, 1]],
        [[37, 0], [41, 1], [43, 1], [44, 1], [61, 0], [62, 1], [62, 1]],
        [[37, 1], [41, 1], [43, 1], [44, 1], [61, 0], [62, 1], [62, 1]],
        [[45, 0], [53, 0], [57, 0], [59, 0], [61, 1], [62, 1], [62, 1]],
        [[45, 1], [53, 0], [57, 0], [59, 0], [61, 1], [62, 1], [62, 1]],
        [[46, 0], [53, 1], [57, 0], [59, 0], [61, 1], [62, 1], [62, 1]],
        [[46, 1], [53, 1], [57, 0], [59, 0], [61, 1], [62, 1], [62, 1]],
        [[47, 0], [54, 0], [57, 1], [59, 0], [61, 1], [62, 1], [62, 1]],
        [[47, 1], [54, 0], [57, 1], [59, 0], [61, 1], [62, 1], [62, 1]],
        [[48, 0], [54, 1], [57, 1], [59, 0], [61, 1], [62, 1], [62, 1]],
        [[48, 1], [54, 1], [57, 1], [59, 0], [61, 1], [62, 1], [62, 1]],
        [[49, 0], [55, 0], [58, 0], [59, 1], [61, 1], [62, 1], [62, 1]],
        [[49, 1], [55, 0], [58, 0], [59, 1], [61, 1], [62, 1], [62, 1]],
        [[50, 0], [55, 1], [58, 0], [59, 1], [61, 1], [62, 1], [62, 1]],
        [[50, 1], [55, 1], [58, 0], [59, 1], [61, 1], [62, 1], [62, 1]],
        [[51, 0], [56, 0], [58, 1], [59, 1], [61, 1], [62, 1], [62, 1]],
        [[51, 1], [56, 0], [58, 1], [59, 1], [61, 1], [62, 1], [62, 1]],
        [[52, 0], [56, 1], [58, 1], [59, 1], [61, 1], [62, 1], [62, 1]],
        [[52, 1], [56, 1], [58, 1], [59, 1], [61, 1], [62, 1], [62, 1]], 
    ]
    output = [[i, i] for i in range(63)]
    i=0
    entry = m.get_entry(entryID)
    current_path = os.path.dirname(__file__)
    file_path = r'team_data/shorthand_names.json'
    shorthand_name_path = os.path.join(current_path, file_path)
    shorthand_names = json.load(open(shorthand_name_path, "r"))
    for semi_final_pairings in m.bracket_pairings:
        for region in semi_final_pairings:
            picks = entry.team_picks[region]
            for team_seed in team_ordering:
                for team in picks[str(team_seed)]:
                    if picks[str(team_seed)][team] > 0:
                        wins = picks[str(team_seed)][team]
                        if team in shorthand_names and wins>=5:
                            team_name = str(team_seed)+' '+shorthand_names[team]
                        else:
                            team_name = str(team_seed)+' '+team

                        output[new_team_paths[i][wins-1][0]][new_team_paths[i][wins-1][1]] = html.Div(
                            team_name, id='game'+str(i)+'-team'+str(new_team_paths[i][wins-1][1]+1), className='team rnd'+str(wins))
                        for j in range(wins-2, -1, -1):
                            if team in shorthand_names and j>=4:
                                team_name = str(team_seed)+' '+shorthand_names[team]
                            else:
                                team_name = str(team_seed)+' '+team
                            output[new_team_paths[i][j][0]][new_team_paths[i][j][1]] = html.Div(
                            team_name, id='game'+str(i)+'-team'+str(new_team_paths[i][j][1]+1), className='team-win team rnd'+str(j+1))
                        i+=1
    return output

@app.callback(
    [Output(component_id='bracket-dropdown', component_property='options'),
     Output(component_id='ranking-graph', component_property='figure'),
     Output(component_id='winning-score-graph', component_property='figure'),
    ],
    [Input(component_id='scoring-table', component_property='data'),
     Input(component_id='scoring-table', component_property='selected_rows'),
     Input('hidden-dataframe', 'children')]
)
# Update dropdown and also graphs with new entries
def update_dropdown(data, entryID, json_filtered_dataframe):
    filtered_dataframe = pd.read_json(json_filtered_dataframe, orient='split')
    dropdown_options=[{'label': data[row]['Entry'], 'value': data[row]['Index']} for row in entryID]
    filtered_special_results = filtered_dataframe[-4:]
    filtered_entry_results = filtered_dataframe[:-4]
    index_list = [data[entry]['Index'] for entry in entryID]
    filtered_results = filtered_dataframe[filtered_dataframe['entryID'].isin(index_list)]
    ranks_figure = prepare_ranks_graph(filtered_results)

    winning_score_figure = prepare_scores_graph(filtered_results)
    # m.raw_print()
    return dropdown_options,ranks_figure, winning_score_figure

if __name__ == '__main__':
    # app.run_server(debug=True, use_reloader=True)
    app.run_server(debug=False, use_reloader=False)

