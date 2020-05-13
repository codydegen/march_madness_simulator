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
                                    show_curve=True, show_hist=True, bin_size=1, 
                                    histnorm='probability')
    except:
        print('Singular matrix error')
        for i in range(len(most_valuable_rank)):
            # Following code is potentially needed to prevent singular matrix error
            if most_valuable_rank[i] == most_popular_rank[i] and most_valuable_rank[i] == chalk_rank[i]:
                print(' I decay')
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
                                show_curve=True, bin_size=10, 
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
        return round(i/sims*100, 3)

    def convert_entry_to_dictionary(dataframe, name):
        ranks = get_array_from_dataframe(dataframe, 'placings', name)
        ranks.sort()
        index = dataframe[dataframe['name'] == name]['entryID'].values[0]
        entry = {
            'Index': index,
            'Entry': name,
            'First Places': get_sub_placings(ranks, 1),
            'Second Places': get_sub_placings(ranks, 2),
            'Third Places': get_sub_placings(ranks, 3),
            'Top Five': get_sub_placings(ranks, 5, inclusive=True),
            'Top Ten': get_sub_placings(ranks, 10, inclusive=True),
            'Top 5%': get_sub_placings(ranks, 5, percentile=True),
            'Average Placing': get_sub_placings(ranks, 0, average=True),
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
def create_region(region, stages):
    stage_html_list=[]
    for stage in stages:
        game_html_list = []
        for i in range(stages[stage]):
            game_html_list.append(html.Div([
                html.Div(region+' '+stage+' g'+str(i)+' 1', id=region+'-'+stage+'-g'+str(i)+'-team1', className='team team1'),
                html.Div(region+' '+stage+' g'+str(i)+' 2', id=region+'-'+stage+'-g'+str(i)+'-team2', className='team team2'),
            ], className=region+' '+stage+' g'+str(i)+' game'))
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
    left_region_html_list.append(create_region('r1', stages))
    left_region_html_list.append(create_region('r2', stages))
    right_region_html_list = []
    right_region_html_list.append(create_region('r3', stages))
    right_region_html_list.append(create_region('r4', stages))
    bounding_html_list.append(
        html.Div(left_region_html_list, className='left-bounding')
    )
    bounding_html_list.append(
        html.Div([html.Div([
            html.Div('ff g1 1', id='n4-g0-team1', className='team team1'),
            html.Div('ff g1 2', id='n4-g0-team2', className='team team2'),
        ], className='n4 g1')], className='final-four-bounding inner-bounding game')
    )
    bounding_html_list.append(
        html.Div([html.Div([
            html.Div('f g1 1', id='n2-g0-team1', className='team team1'),
            html.Div('f g1 2', id='n2-g0-team2', className='team team2'),
        ], className='n2 g1')], className='finals-bounding inner-bounding game')
    )
    bounding_html_list.append(
        html.Div([html.Div([
            html.Div('ff g2 1', id='n4-g1-team1', className='team team1'),
            html.Div('ff g2 2', id='n4-g1-team2', className='team team2'),
        ], className='n4 g2')], className='final-four-bounding inner-bounding game')
    )
    bounding_html_list.append(
        html.Div(right_region_html_list, className='right-bounding')
    )
    bracket_html = html.Div(bounding_html_list, className='bounding-bracket')
    return bracket_html


###############################################################################
################################ Global code ##################################
###############################################################################
number_simulations = 1000
number_entries = 100
year = 2019
gender = "mens"
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
table_columns=['Entry', 'First Places', 'Second Places', 'Third Places', 'Top Five', 'Top Ten', 'Top 5%', 'Average Placing']
# sub_results = random_subsample(number_entries)
figures = [
    dt.DataTable(
        id="scoring-table",
        columns=[{"name": i, "id": i} for i in table_columns],
        data=prepare_table(entry_results, special_results, number_entries),
        editable=True,
        row_selectable='single',
        selected_rows=[0],
        sort_action='native',
        ),
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
        for region in regions:
            for stage in stages:
                for i in range(stages[stage]):
                    output_list.append(Output(component_id='r'+str(region_number)+'-'+stage+'-g'+str(i)+'-'+'team1', component_property='children'))
                    # output_list.append(Output(component_id='r'+str(region_number)+'-'+stage+'-g'+str(i)+'-'+'team1', component_property='className'))
                    output_list.append(Output(component_id='r'+str(region_number)+'-'+stage+'-g'+str(i)+'-'+'team2', component_property='children'))
                    # output_list.append(Output(component_id='r'+str(region_number)+'-'+stage+'-g'+str(i)+'-'+'team2', component_property='className'))
            region_number+=1

    def populate_sublist_final_four(output_list):
        game_ids = ['n4-g0', 'n2-g0', 'n4-g1']
        for game_id in game_ids:
            output_list.append(Output(component_id=game_id+'-team1', component_property='children'))
            # output_list.append(Output(component_id=game_id+'-team1', component_property='className'))
            output_list.append(Output(component_id=game_id+'-team2', component_property='children'))
            # output_list.append(Output(component_id=game_id+'-team2', component_property='className'))

    populate_sublist_region(output_list, left_regions, 1)
    populate_sublist_final_four(output_list)
    populate_sublist_region(output_list, right_regions, 3)
    return output_list
output_list = create_output_list_for_bracket_callback()

@app.callback(
    output_list, 
    [Input(component_id='scoring-table', component_property='data'),
     Input(component_id='scoring-table', component_property='selected_rows')],
    # [State("scoring-table", "data")]
)
def fill_bracket_visualization(data, entryID):
    if entryID == None:
        return [str(i) for i in range(126)]
    team_paths_index = 0
    team_ordering = [1, 16, 8, 9, 5, 12, 4, 13, 6, 11, 3, 14, 7, 10, 2, 15]
    team_paths = [
        [0, 16, 24, 28, 60, 62],
        [1, 16, 24, 28, 60, 62],
        [2, 17, 24, 28, 60, 62],
        [3, 17, 24, 28, 60, 62],
        [4, 18, 25, 28, 60, 62],
        [5, 18, 25, 28, 60, 62],
        [6, 19, 25, 28, 60, 62],
        [7, 19, 25, 28, 60, 62],
        [8, 20, 26, 29, 60, 62],
        [9, 20, 26, 29, 60, 62],
        [10, 21, 26, 29, 60, 62],
        [11, 21, 26, 29, 60, 62],
        [12, 22, 27, 29, 60, 62],
        [13, 22, 27, 29, 60, 62],
        [14, 23, 27, 29, 60, 62],
        [15, 23, 27, 29, 60, 62],
        [30, 46, 54, 58, 61, 62],
        [31, 46, 54, 58, 61, 62],
        [32, 47, 54, 58, 61, 62],
        [33, 47, 54, 58, 61, 62],
        [34, 48, 55, 58, 61, 62],
        [35, 48, 55, 58, 61, 62],
        [36, 49, 55, 58, 61, 62],
        [37, 49, 55, 58, 61, 62],
        [38, 50, 56, 59, 61, 62],
        [39, 50, 56, 59, 61, 62],
        [40, 51, 56, 59, 61, 62],
        [41, 51, 56, 59, 61, 62],
        [42, 52, 57, 59, 61, 62],
        [43, 52, 57, 59, 61, 62],
        [44, 53, 57, 59, 61, 62],
        [45, 53, 57, 59, 61, 62],
        [66, 82, 90, 94, 64, 63],
        [67, 82, 90, 94, 64, 63],
        [68, 83, 90, 94, 64, 63],
        [69, 83, 90, 94, 64, 63],
        [70, 84, 91, 94, 64, 63],
        [71, 84, 91, 94, 64, 63],
        [72, 85, 91, 94, 64, 63],
        [73, 85, 91, 94, 64, 63],
        [74, 86, 92, 95, 64, 63],
        [75, 86, 92, 95, 64, 63],
        [76, 87, 92, 95, 64, 63],
        [77, 87, 92, 95, 64, 63],
        [78, 88, 93, 95, 64, 63],
        [79, 88, 93, 95, 64, 63],
        [80, 89, 93, 95, 64, 63],
        [81, 89, 93, 95, 64, 63],
        [96, 112, 120, 124, 65, 63],
        [97, 112, 120, 124, 65, 63],
        [98, 113, 120, 124, 65, 63],
        [99, 113, 120, 124, 65, 63],
        [100, 114, 121, 124, 65, 63],
        [101, 114, 121, 124, 65, 63],
        [102, 115, 121, 124, 65, 63],
        [103, 115, 121, 124, 65, 63],
        [104, 116, 122, 125, 65, 63],
        [105, 116, 122, 125, 65, 63],
        [106, 117, 122, 125, 65, 63],
        [107, 117, 122, 125, 65, 63],
        [108, 118, 123, 125, 65, 63],
        [109, 118, 123, 125, 65, 63],
        [110, 119, 123, 125, 65, 63],
        [111, 119, 123, 125, 65, 63],
    ]
    output = [i for i in range(126)]
    # output = str(entryID),
    entry = m.get_entry(data[entryID[0]]['Index'])
    for semi_final_pairings in m.bracket_pairings:
        for region in semi_final_pairings:
            picks = entry.team_picks[region]
            for i in team_ordering:
                for team in picks[str(i)]:
                    if picks[str(i)][team] > 0:
                        team_name = str(i)+' '+team
                        wins = picks[str(i)][team]
                        output[team_paths[team_paths_index][0]] = team_name
                        for j in range(1, wins):
                            if j < 6:
                                game_number = team_paths[team_paths_index][j]
                                output[game_number] = team_name
                            won_game_number = team_paths[team_paths_index][j-1]
                            output[won_game_number] = team_name+' w'
                            
                team_paths_index+=1
            # output=str(picks['1'])
    return output



if __name__ == '__main__':
    # model.main()
    print("t")
    # app.run_server(debug=True)
    app.run_server(debug=False, use_reloader=True)

