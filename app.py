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
# app.layout = html.Div(children=[
#     html.H1(children='Hello Dash')]
#     )
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
                most_valuable_rank[i] += most_valuable_rank[i]+.0000000001
        figure = ff.create_distplot(hist_data, group_labels, show_rug=False, 
                            show_curve=True, show_hist=True, bin_size=1, 
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

    def get_placings(place, inclusive=False, percentile=False, average=False):

        def get_sub_placings(data_set, place, inclusive, percentile, average):
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
            return str(round(i/sims*100, 1))+"%"
            
        score_array = []
        score_array.append(get_sub_placings(most_valuable_rank, place, inclusive, percentile, average))
        score_array.append(get_sub_placings(most_popular_rank, place, inclusive, percentile, average))
        score_array.append(get_sub_placings(chalk_rank, place, inclusive, percentile, average))
        return score_array

    # Get rankings and then sort them
    # TODO this could eventually be modularized using a dictionary to allow 
    # additional entries to be added to the table
    most_valuable_rank = get_array_from_dataframe(special_results, 'placings', 'most_valuable_teams')
    most_valuable_rank.sort()
    most_popular_rank = get_array_from_dataframe(special_results, 'placings', 'most_popular_teams')
    most_popular_rank.sort()
    chalk_rank = get_array_from_dataframe(special_results, 'placings', 'chalk')
    chalk_rank.sort()

    bracket_type = ['Most Valuable Teams', 'Most Popular Teams', 'Chalk']
    # Get placings for various positions
    first_places = get_placings(1)
    second_places = get_placings(2)
    third_places = get_placings(3)
    top_fives = get_placings(5,inclusive=True)
    top_tens = get_placings(10,inclusive=True)
    top_five_percentile = get_placings(5, percentile=True)
    average = get_placings(0, average=True)

    columns = dict(values=['Bracket Type', '1st Places', '2nd Places', '3rd Places', 'Top 5', 'Top 10', 'Top 5%', 'Average Placing'],
                    align=['center','center'],
                    )
    cells = dict(values=[bracket_type, first_places, second_places, third_places, top_fives, top_tens, top_five_percentile, average],
                align=['center','center'],
                height=30,
                )
    # figure = go.Figure(data=[go.Table(name="Rankings",
    #                                 header=columns, 
    #                                 cells=cells,
    #                                 columnwidth=[80,40,40,40,40,40,40,40
    # ])])
    a = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')
    figure = dt.DataTable(
        id="scoring-table",
        columns=[{"name": i, "id": i} for i in a.columns],
        data=a.to_dict('records'),
        editable=True,
        active_cell={"row": 0, "column": 0},
        selected_cells=[{"row": 0, "column": 0}],
        )
    return figure

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
    #  Output(component_id='scoring-table', component_property='figure'),
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
    return ranks_figure, winning_score_figure
    # return ranks_figure, scoring_table, winning_score_figure

# Create the outline of the bracket used for visualizations
def create_bracket():

    # Create each individual region
    def create_region(region):
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
    left_region_html_list.append(create_region('r1'))
    left_region_html_list.append(create_region('r2'))
    right_region_html_list = []
    right_region_html_list.append(create_region('r3'))
    right_region_html_list.append(create_region('r4'))
    bounding_html_list.append(
        html.Div(left_region_html_list, className='left-bounding')
    )
    bounding_html_list.append(
        html.Div([html.Div([
            html.Div('ff g1 1', id='n4-g0-team1', className='team team1'),
            html.Div('ff g1 2', id='n4-g0-team2', className='team team2'),
        ], className='n4 g1')], className='final-four-bounding game')
    )
    bounding_html_list.append(
        html.Div([html.Div([
            html.Div('f g1 1', id='n2-g0-team1', className='team team1'),
            html.Div('f g1 2', id='n2-g0-team2', className='team team2'),
        ], className='n2 g1')], className='finals-bounding game')
    )
    bounding_html_list.append(
        html.Div([html.Div([
            html.Div('ff g2 1', id='n4-g1-team1', className='team team1'),
            html.Div('ff g2 2', id='n4-g1-team2', className='team team2'),
        ], className='n4 g2')], className='final-four-bounding game')
    )
    bounding_html_list.append(
        html.Div(right_region_html_list, className='right-bounding')
    )
    bracket_html = html.Div(bounding_html_list, className='bounding-bracket')
    return bracket_html

@app.callback(
    [Output(component_id='n2-g0-team1', component_property='children')], 
    [Input(component_id='scoring-table', component_property='active_cell')],
    # [State("scoring-table", "data")]
)
def fill_bracket_visualization(entryID):
    output = str(entryID),
    return output
    # [html.Div(str(entryID), id='n2-g0-team2', className='team team2')]
    entry = m.get_entry(-2)
    i=0
    for semi_final_pairings in m.bracket_pairings:

        for region in semi_final_pairings:
            picks = entry.team_picks[region]
            output=str(picks['1'])
            return [output,]
            pass
    # Go through each region
    # Fill each region and based on the number of wins
    # Team with six wins wins their final four matchup
    # Team with seven wins wins the entire thing
    pass


number_simulations = 20
number_entries = 5
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
# fill_bracket_visualization(-2)
# sub_results = m.analyze_sublist(number_sub_sims, number_subteams)

# sub_results = random_subsample(number_entries)
figures = [
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
figures.append(prepare_table(entry_results, special_results, number_simulations))
figures.append(dcc.Graph(
    id='winning-score-graph',
    figure=prepare_scores_graph(entry_results, special_results)))

app.layout = html.Div(figures)

if __name__ == '__main__':
    # model.main()
    print("t")
    # app.run_server(debug=True)
    app.run_server(debug=True, use_reloader=True)

