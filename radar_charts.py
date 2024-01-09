#Radar Charts in streamlit

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import percentileofscore
import plotly.express as px


def radar_chart(player_name):
    filepath = '/Users/rohitkrishnan/Desktop/2023stats.csv'
    all_data = pd.read_csv(filepath, skiprows=1)
    all_data["Minor_Possessions"] = all_data['FGA'] + 0.44 * all_data['FTA'] + all_data['TOV']
    all_data["Major_Possessions"] = all_data['FGA'] + 0.44 * all_data['FTA'] - all_data['OREB'] + all_data['TOV']

    team_assists = all_data.groupby('Team')['AST'].sum()
    team_made_field_goals = all_data.groupby('Team')['FGM'].sum()

    # Next, calculate the ratio of assists to made field goals for each team
    team_assists_to_made_field_goals = team_assists / team_made_field_goals

    # Merge the calculated ratio back into the 'team_stats' DataFrame
    all_data = pd.merge(all_data, team_assists_to_made_field_goals.rename('TmAst_TmFGM'), left_on='Team', right_index=True)

    num_players = 5 
    player_min = 24

    # Step 1: Calculate individual player's assists per minute (Ast/Min)
    all_data['Ast_Per_Min'] = all_data['AST'] / player_min

    # Step 2: Calculate team's average assists per minute (TmAst/(TmMin/5))
    team_avg_ast_per_min = all_data.groupby('Team').apply(lambda x: x['AST'].sum() / (len(x) * player_min)).reset_index()
    team_avg_ast_per_min.columns = ['Team', 'Tm_Avg_Ast_Per_Min']

    # Step 3: Merge the team's average assists per minute back into the 'all_data' DataFrame
    all_data = pd.merge(all_data, team_avg_ast_per_min, on='Team', how='left')

    # Step 4: Calculate the desired ratio (Ast/Min relative to TmAst/(TmMin/5))
    all_data['Ratio_Ast_Per_Min'] = all_data['Ast_Per_Min'] / all_data['Tm_Avg_Ast_Per_Min']

    # Step 1: Calculate individual player's offensive rebounds per minute (OReb/Min)
    all_data['OReb_Per_Min'] = all_data['OREB'] / player_min

    # Step 2: Calculate the number of offensive rebounds per 48 minutes
    all_data['Off_Reb_Per_48_Min'] = all_data['OReb_Per_Min'] * 48

    # Step 1: Calculate individual player's Usage using 'Major_Possessions'
    all_data['Usage'] = all_data['Major_Possessions'] / (player_min / num_players)

    # Step 1: Calculate (3A/FGA)^2
    all_data['Three_Point_Efficiency'] = (all_data['FG3A'] / all_data['FGA']) ** 2

    # Step 3: Calculate (1/Usage)^2
    all_data['Usage_Efficiency'] = (1 / all_data['Usage']) ** 2

    # Step 4: Calculate the final shooting efficiency metric
    all_data['Shooting_Efficiency'] = all_data['Three_Point_Efficiency'] * all_data['Usage_Efficiency']

    # Calculate the complete formula with an absolute value
    all_data['Complete_Formula'] = abs(all_data['TmAst_TmFGM'] * (1.53 - 1.442 * (all_data['Ast_Per_Min'] / all_data['Tm_Avg_Ast_Per_Min']) - 
                                                        0.041 * ((all_data['OREB'] / player_min) * 48) - 
                                                        0.787 * all_data['Usage'] + 
                                                        0.014 * all_data['Shooting_Efficiency']))

    # Step 9: Calculate Points Created (PC) using the 'Complete_Formula' column
    all_data['PC'] = all_data['Complete_Formula'] * all_data['FGM'] * 0.75

    # Step 10: Calculate the estimated assisted field goals (Afgm)
    all_data['Afgm'] = all_data['AST'] * 0.5

    # Step 11: Calculate Possessions (Pos) using the formula provided
    all_data['Pos'] = all_data['FGA'] + (0.44 * all_data['FTA']) + all_data['TOV'] + (0.375 * all_data['AST']) - all_data['Afgm']

    # Step 12: Calculate Offensive Rating
    all_data['Offensive_Rating'] = (all_data['PC'] / all_data['Pos']) * 100

    all_data["PPG"] = all_data["PTS"] / all_data["GP"]

    all_data["OER"] = all_data["PF"] / (all_data["FGA"] - all_data["OREB"] + all_data["TOV"] + 0.44 * all_data["FTA"])

def point_guards():
    #League Data & then just PG data:
    filepath = '/Users/rohitkrishnan/Desktop/2023stats.csv'
    all_data = pd.read_csv(filepath, skiprows=1)

    # Step 1: Data Preparation
    numeric_columns = ['PTS', 'AST', 'FT%', 'FTA', 'FTM', 'FG3%', 'FG3A', 'FG3M', 'FG%', 'FGA', 'FGM', 'PPG', 'STL', 'Complete_Formula']
    # Fix this for Point Guard Data Set only
    #top_point_guards = all_data[all_data['Pos.'] == 'PG'].nlargest(30, 'PPG')
    league_data = all_data[numeric_columns]

    # Create angles for radar chart
    angles = np.linspace(0, 2 * np.pi, len(numeric_columns), endpoint=False)
    angles = np.concatenate((angles, [angles[0]]))

    # Create an empty list to store radar charts
    radar_charts = []


# Loop through each top point guard and create radar charts. 
# Fix for PGs. 
    for index, player_row in top_point_guards.iterrows():
        player_name = player_row['Player']
    
        # Calculate percentile ranks for the selected player
        player_data = player_row[numeric_columns]
        percentile_ranks_player = [percentileofscore(league_data[column], player_data[column]) for column in numeric_columns]
        percentile_ranks_player = [rank / 100 for rank in percentile_ranks_player]  # Convert to floats
        
        # Calculate average values and percentile ranks for remaining point guards
        avg_point_guards = top_point_guards[top_point_guards['Player'] != player_name][numeric_columns].mean()
        percentile_ranks_avg = [percentileofscore(league_data[column], avg_point_guards[column]) for column in numeric_columns]
        percentile_ranks_avg = [rank / 100 for rank in percentile_ranks_avg]  # Convert to floats
        
        # Create the radar chart
        fig = plt.figure(figsize=(12, 9))
        ax = plt.subplot(111, polar=True)
        ax.plot(angles, percentile_ranks_player + [percentile_ranks_player[0]], linewidth=2, label=player_name)
        ax.fill(angles, percentile_ranks_player + [percentile_ranks_player[0]], alpha=0.25)
        ax.plot(angles, percentile_ranks_avg + [percentile_ranks_avg[0]], linewidth=2, label='Avg Point Guards')
        plt.xticks(angles[:-1], numeric_columns, color='grey', size=8)
        plt.yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='grey', size=7)
        plt.title(f'{player_name} vs. Avg Point Guards Percentile Comparison')
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    
        # Append the radar chart to the list
        radar_charts.append((player_name, fig))
        return fig
    
new_file = '/Users/rohitkrishnan/Desktop/2023stats.csv'
data = pd.read_csv(new_file,skiprows=1)
player_names = data['Player'].unique()

def dropdown (): 
    # Add a dropdown to select a player
    selected_player = st.selectbox('Select a Player', player_names)
    # Check if the user has selected a player
    if selected_player:
        # Create a radar chart based on the selected player
        fig = radar_chart(selected_player)
        # Display the radar chart using Streamlit's st.pyplot()
        st.pyplot(fig)
        return (selected_player)
    

# Add a title and intro text
st.title('2KL Data Explorer')
st.text('Web app to allow exploration of 2KL Data')

# Sidebar setup
st.sidebar.title('Navigation')
upload_file = st.sidebar.file_uploader('Upload a file containing 2KL data')
#Sidebar navigation
st.sidebar.title('Navigation')
options = st.sidebar.radio('Select what you want to display:', ['Home', 'Data Summary', 'Data Header', 'Scatter Plot', 'Fancy Plots'])

# Check if file has been uploaded
if upload_file is not None:
    df = pd.read_csv(upload_file)

# Navigation options

if options == 'Radar Charts':
    playerselection = dropdown()
    radar_chart(playerselection)
else: 
    None
