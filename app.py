import model.model as model
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
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

external_stylesheets = ['../assets/styles.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title='March Madness Simulator'
# Helper function
# TODO There is probably a more effective way of doing this in pandas 
def get_array_from_dataframe(frame, array_type, data_type):
    return frame[frame['name']==data_type][array_type].values[0]

# Ranks graph function
def prepare_ranks_graph(entry_results, special_results):
    most_valuable_rank = get_array_from_dataframe(special_results, 'ranks', 'most_valuable_teams')
    most_popular_rank = get_array_from_dataframe(special_results, 'ranks', 'most_popular_teams')
    chalk_rank = get_array_from_dataframe(special_results, 'ranks', 'chalk')
    

    hist_data = [most_valuable_rank, most_popular_rank, chalk_rank]
    group_labels = ['Most Valuable Teams', 'Most Popular Teams', 'Chalk']
    try:
        figure = ff.create_distplot(hist_data, group_labels, show_rug=False, 
                                    show_curve=False, show_hist=True, bin_size=1, 
                                    histnorm='probability')
    except:
        print('Singular matrix error')
        for i in range(len(most_valuable_rank)):
            # Following code is potentially needed to prevent singular matrix error
            if most_valuable_rank[i] == most_popular_rank[i] and most_valuable_rank[i] == chalk_rank[i]:
                print('IDK')
                most_valuable_rank[i] += .0000000001
                most_popular_rank[i] -= .0000000001
                chalk_rank[i] += .000000001

        figure = ff.create_distplot(hist_data, group_labels, show_rug=False, 
                            show_curve=False, show_hist=True, bin_size=1, 
                            histnorm='probability')
    figure.update_layout(
        title_text='Histogram of Final Placements',
        xaxis_title='Placing',
        yaxis_title='Share of Simulations'
    )
    return figure

# Scores graph function
def prepare_scores_graph(entry_results, special_results):
    overall_winning_score_values = get_array_from_dataframe(special_results, 'simulations', 'winning_score')
    chalk_values = get_array_from_dataframe(special_results, 'simulations', 'chalk')
    most_valuable_values = get_array_from_dataframe(special_results, 'simulations', 'most_valuable_teams')
    most_popular_values = get_array_from_dataframe(special_results, 'simulations', 'most_popular_teams')

    hist_data = [overall_winning_score_values, chalk_values, most_valuable_values, most_popular_values]
    group_labels = ['Winning Score', 'Chalk', 'Most Valuable', 'Most Popular']
    figure = ff.create_distplot(hist_data, group_labels, show_rug=False, 
                                show_curve=False, bin_size=10, 
                                histnorm='probability')
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
        percentiles = [get_sub_placings(ranks, 20, percentile=True), 
                       get_sub_placings(ranks, 40, percentile=True), 
                       get_sub_placings(ranks, 60, percentile=True), 
                       get_sub_placings(ranks, 80, percentile=True), 
                       1]
        entry = {
            'Index': index,
            'Entry': name,
            '1st': get_sub_placings(ranks, 1),
            '2nd': get_sub_placings(ranks, 2),
            '3rd': get_sub_placings(ranks, 3),
            # 'Top Five': get_sub_placings(ranks, 5, inclusive=True),
            # 'Top Ten': get_sub_placings(ranks, 10, inclusive=True),
            '1st Q.': percentiles[0],
            '2nd Q.': percentiles[1]-percentiles[0],
            '3rd Q.': percentiles[2]-percentiles[1],
            '4th Q.': percentiles[3]-percentiles[2],
            '5th Q.': percentiles[4]-percentiles[3],
            'Avg Plc.': get_sub_placings(ranks, 0, average=True),
        }
        return entry
    # Get rankings and then sort them

    # most_valuable_rank = get_array_from_dataframe(special_results, 'placings', 'most_valuable_teams')
    # most_valuable_rank.sort()
    # most_popular_rank = get_array_from_dataframe(special_results, 'placings', 'most_popular_teams')
    # most_popular_rank.sort()
    # chalk_rank = get_array_from_dataframe(special_results, 'placings', 'chalk')
    # chalk_rank.sort()

    data_array = []
    data_array.append(convert_entry_to_dictionary(special_results, 'most_valuable_teams'))
    data_array.append(convert_entry_to_dictionary(special_results, 'most_popular_teams'))
    data_array.append(convert_entry_to_dictionary(special_results, 'chalk'))
    for entry in entry_results['name']:
        data_array.append(convert_entry_to_dictionary(entry_results, entry))

    print("updating table viz")
    return data_array

def prepare_number_entries_input():
    entries_input = dcc.Input(
        id='number-entries-input',
        type='number',
        value=number_entries,
        max=number_entries,
        min=0
    )
    return entries_input 

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
    button = html.Button(id='run-input', n_clicks=0, children='Rerun Analysis')
    return button

# Call back to update once results change
@app.callback(
    [Output(component_id='ranking-graph', component_property='figure'),
     Output(component_id='scoring-table', component_property='data'),
     Output(component_id='scoring-table', component_property='selected_rows'),
     Output(component_id='winning-score-graph', component_property='figure')],
    [Input(component_id='run-input', component_property='n_clicks')],
    [State('number-entries-input', 'value'),
     State('number-simulations-input', 'value')])
def update_table(n_clicks, entry_input, simulations_input):
    filtered_dataframe = m.analyze_sublist(all_results, entry_input, simulations_input)
    filtered_special_results = filtered_dataframe[-4:]
    filtered_entry_results = filtered_dataframe[:-4]
    ranks_figure = prepare_ranks_graph(filtered_entry_results, filtered_special_results)
    scoring_table = prepare_table(filtered_entry_results, filtered_special_results, simulations_input)
    winning_score_figure = prepare_scores_graph(filtered_entry_results, filtered_special_results)
    print("update complete")
    return ranks_figure, scoring_table, [0], winning_score_figure

# Create each individual region
def create_region(region, stages, initial_game_number):
    stage_html_list=[]
    for stage in stages:
        game_html_list = []
        for i in range(stages[stage]):
            game_html_list.append(html.Div([
                html.Div('game'+str(initial_game_number)+' 1', id='game'+str(initial_game_number)+'-team1', className='team team1'),
                html.Div('game'+str(initial_game_number)+' 2', id='game'+str(initial_game_number)+'-team2', className='team team2'),
            ], id='game'+str(initial_game_number), className=region+' '+stage+' g'+str(i)+' game'))
            initial_game_number+=1
        stage_html_list.append(
            html.Div(game_html_list, className='inner-bounding '+stage))
    return html.Div(stage_html_list, className='bounding-'+region)


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
            html.Div('ff g1 1', id='game60-team1', className='team team1'),
            html.Div('ff g1 2', id='game60-team2', className='team team2'),
        ], className='n4 g1')], id='game60', className='final-four-bounding inner-bounding game')
    )
    bounding_html_list.append(
        html.Div([html.Div([
            html.Div('f g1 1', id='game62-team1', className='team team1'),
            html.Div('f g1 2', id='game62-team2', className='team team2'),
        ], className='n2 g1')], id='game62', className='finals-bounding inner-bounding game')
    )
    bounding_html_list.append(
        html.Div([html.Div([
            html.Div('ff g2 1', id='game61-team1', className='team team1'),
            html.Div('ff g2 2', id='game61-team2', className='team team2'),
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
number_simulations = 12
number_entries = 10
year = 2019
gender = "womens"
m = model.Model(number_simulations=number_simulations, gender=gender, scoring_sys="ESPN", year=year)
m.batch_simulate()
print("sims done")
m.create_json_files()
m.update_entry_picks()
m.initialize_special_entries()
m.analyze_special_entries()
m.add_bulk_entries_from_database(number_entries)
m.add_simulation_results_postprocessing()


all_results = m.output_results()
special_wins = m.get_special_wins()
special_results = all_results[-4:]
entry_results = all_results[:-4]
table_columns_pre=['Entry']
table_columns_places=['1st', '2nd', '3rd'] 
table_columns_quintiles=['1st Q.', '2nd Q.', '3rd Q.', '4th Q.', '5th Q.']
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

table_data = prepare_table(entry_results, special_results, number_entries)
# sub_results = random_subsample(number_entries)
figures = [
    dt.DataTable(
        id="scoring-table",
        columns=[{"name": i, "id": i} for i in table_columns_pre]+ 
                [{"name": i, "id": i, "type": "numeric", "format": FormatTemplate.percentage(1)} for i in table_columns_places] + 
                [{"name": i, "id": i, "type": "numeric", "format": FormatTemplate.percentage(1)} for i in table_columns_quintiles] +
                [{"name": i, "id": i} for i in table_columns_post],
        data=table_data,
        # editable=True,
        # virtualization=True,
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
                                        'filter_query': '{Index} < 4',  # matching rows of a hidden column with the id, `id`
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
    html.Div([
    dcc.Dropdown(
        id='bracket-dropdown',
        options=[
            {'label': 'most_popular_teams', 'value': -3},
        ],
        value=-3,
        # clearable=False
    ),]),

    create_bracket(), 
    html.H1('Simulation Of '+gender.capitalize()[:-1]+'\'s March Madness Brackets: '+str(year)),
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
        ], className="bounding-box"),
    html.Div([
        prepare_run_button_input(),
    ], className="run-button"),
]
figures.append(dcc.Graph(
    id='ranking-graph',
    figure=prepare_ranks_graph(entry_results, special_results)))
# figures.append(prepare_table(entry_results, special_results, number_simulations))
figures.append(dcc.Graph(
    id='winning-score-graph',
    figure=prepare_scores_graph(entry_results, special_results)))

app.layout = html.Div(figures)

def create_output_list_for_bracket_callback():
    stages = {
        'n64' : 8, 
        'n32' : 4,
        'n16' : 2,
        'n8' : 1
    }
    output_list = []
    # left_output_list = []
    # right_output_list = []
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
output_list = create_output_list_for_bracket_callback()

@app.callback(
    output_list, 
    [Input('bracket-dropdown', 'value')],
    # [State("scoring-table", "data")]
)
def fill_bracket_visualization(entryID):
    if entryID == []:
        print(' no entry ID provided')
        output = [[html.Div('', id='game'+str(i)+'-team1', className='team team1 rnd1'),
                   html.Div('', id='game'+str(i)+'-team2', className='team team2 rnd1'),
    ] for i in range(63)]
        return output
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
    #! output = [[html.Div('game'+str(i)+' 1', id='game'+str(i)+'-team1', className='team team1 '),
    #            html.Div('game'+str(i)+' 2', id='game'+str(i)+'-team2', className='team team2 '),
    # ] for i in range(63)]
    output = [[i, i] for i in range(63)]
    i=0
    # entry = m.get_entry(data[entryID[0]]['Index'])
    entry = m.get_entry(entryID)
    for semi_final_pairings in m.bracket_pairings:
        for region in semi_final_pairings:
            picks = entry.team_picks[region]
            for team_seed in team_ordering:
                for team in picks[str(team_seed)]:
                    if picks[str(team_seed)][team] > 0:
                        team_name = str(team_seed)+' '+team
                        wins = picks[str(team_seed)][team]
                        output[new_team_paths[i][wins-1][0]][new_team_paths[i][wins-1][1]] = html.Div(
                            team_name, id='game'+str(i)+'-team'+str(new_team_paths[i][wins-1][1]+1), className='team rnd'+str(wins))
                        for j in range(wins-2, -1, -1):
                            output[new_team_paths[i][j][0]][new_team_paths[i][j][1]] = html.Div(
                            team_name, id='game'+str(i)+'-team'+str(new_team_paths[i][j][1]+1), className='team-win team rnd'+str(j+1))
                        i+=1
    return output

@app.callback(
    [Output(component_id='bracket-dropdown', component_property='options'),
    #  Output(component_id='ranking-graph', component_property='figure'),
    #  Output(component_id='winning-score-graph', component_property='figure'),
    ],
    [Input(component_id='scoring-table', component_property='data'),
     Input(component_id='scoring-table', component_property='selected_rows')]
)
# Update dropdown and also graphs with new entries
def update_dropdown(data, entryID):
    dropdown_options=[{'label': data[row]['Entry'], 'value': data[row]['Index']} for row in entryID]

    return [dropdown_options]#, ranking_graph, winning_score_graph

if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(debug=True, use_reloader=True)

