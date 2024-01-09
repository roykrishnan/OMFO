import streamlit as st
from streamlit_extras.app_logo import add_logo
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import percentileofscore

add_logo("images/liquid_logo.png", height = 65)

# Load Data
filepath = 'data/2023stats.csv'
all_data = pd.read_csv(filepath, skiprows=1)
st.sidebar.image("images/small_logo.png", caption="Developed and Maintained by Roy Krishnan")


# Select Position
position = st.sidebar.multiselect(
    "Select Position: ",
    options=all_data["Pos."].unique(),
    max_selections=1,
    default= 'PG',
    key="pos"
)
player1 = st.sidebar.multiselect(
    "Select Player 1: ",
    options=all_data["Player"][all_data["Pos."].isin(position)].unique(),
    max_selections=1,
    key="p1"
)
player2 = st.sidebar.multiselect(
    "Select Player 2: ",
    options=all_data["Player"][all_data["Pos."].isin(position)].unique(),
    max_selections=1,
    key="p2"
)
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

# Step 1: Data Preparation
numeric_columns = ['PTS', 'AST', 'FT%', 'FTA', 'FTM', 'FG3%', 'FG3A', 'FG3M', 'FG%', 'FGA', 'FGM', 'PPG', 'STL', 'Complete_Formula']
league_data = all_data[numeric_columns]

# Create angles for radar chart
angles = np.linspace(0, 2 * np.pi, len(numeric_columns), endpoint=False)
angles = np.concatenate((angles, [angles[0]]))

# Use cases for creating radar charts
if position[0] == 'PG':
    top_point_guards = all_data[all_data['Pos.'] == 'PG']
    if player1:
        player_name = player1[0]
        selected_player_row = top_point_guards[top_point_guards['Player'] == player_name]

        # Calculate percentile ranks for the selected player
        player_data = selected_player_row[numeric_columns]
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
        ax.plot(angles, percentile_ranks_avg + [percentile_ranks_avg[0]], linewidth=2, label= f'Avg {position[0]}')
        plt.xticks(angles[:-1], numeric_columns, color='white', size=8)
        plt.yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        plt.title(f'{player_name} vs. Avg {position[0]}')
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.style.use('dark_background')
        st.subheader(player1[0]+' vs. League Average ' + position[0] + 's in NBA 2K League Season 6')
        st.pyplot(fig)

    if player2:
        player_name = player2[0]
        selected_player_row = top_point_guards[top_point_guards['Player'] == player_name]

        # Calculate percentile ranks for the selected player
        player_data = selected_player_row[numeric_columns]
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
        ax.plot(angles, percentile_ranks_avg + [percentile_ranks_avg[0]], linewidth=2, label=f'Average {position[0]}')
        plt.xticks(angles[:-1], numeric_columns, color='white', size=8)
        plt.yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        plt.title(f'{player_name} vs. Avg ' + position[0]+ ' Percentile Comparison')
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.style.use('dark_background')
        st.subheader(player2[0]+' vs. League Average ' + position[0] + 's in NBA 2K League Season 6')
        st.pyplot(fig)

    if player1 and player2:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 9), subplot_kw={'polar': True})
        st.subheader(player1[0]+' vs. ' + player2[0] + ' side by side comparison at '+ position[0] + ' (Season 6)')
        # Plot for Player 1
        player_name1 = player1[0]
        selected_player_row1 = top_point_guards[top_point_guards['Player'] == player_name1]
        player_data1 = selected_player_row1[numeric_columns]
        percentile_ranks_player1 = [percentileofscore(league_data[column], player_data1[column]) for column in numeric_columns]
        percentile_ranks_player1 = [rank / 100 for rank in percentile_ranks_player1]  # Convert to floats
        ax1.plot(angles, percentile_ranks_player1 + [percentile_ranks_player1[0]], linewidth=2, label=player_name1)
        ax1.fill(angles, percentile_ranks_player1 + [percentile_ranks_player1[0]], alpha=0.25)
        ax1.set_xticks(angles[:-1])
        ax1.set_xticklabels(numeric_columns, color='white', size=8)
        ax1.set_yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        ax1.set_title(f'{player_name1} Percentile Comparison', color='white')
        
        # Plot for Player 2
        player_name2 = player2[0]
        selected_player_row2 = top_point_guards[top_point_guards['Player'] == player_name2]
        player_data2 = selected_player_row2[numeric_columns]
        percentile_ranks_player2 = [percentileofscore(league_data[column], player_data2[column]) for column in numeric_columns]
        percentile_ranks_player2 = [rank / 100 for rank in percentile_ranks_player2]  # Convert to floats
        ax2.plot(angles, percentile_ranks_player2 + [percentile_ranks_player2[0]], linewidth=2, label=player_name2)
        ax2.fill(angles, percentile_ranks_player2 + [percentile_ranks_player2[0]], alpha=0.25)
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(numeric_columns, color='white', size=8)
        ax2.set_yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        ax2.set_title(f'{player_name2} Percentile Comparison', color='white')
        
        # Final adjustments
        plt.subplots_adjust(wspace=0.4)
        plt.style.use('dark_background')
        st.pyplot(fig)
elif position [0] == 'SG':
    top_point_guards = all_data[all_data['Pos.'] == 'SG']
    if player1:
        player_name = player1[0]
        selected_player_row = top_point_guards[top_point_guards['Player'] == player_name]

        # Calculate percentile ranks for the selected player
        player_data = selected_player_row[numeric_columns]
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
        ax.plot(angles, percentile_ranks_avg + [percentile_ranks_avg[0]], linewidth=2, label= f'Avg {position[0]}')
        plt.xticks(angles[:-1], numeric_columns, color='white', size=8)
        plt.yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        plt.title(f'{player_name} vs. Avg {position[0]} Percentile Comparison')
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.style.use('dark_background')
        st.subheader(player1[0]+' vs. League Average ' + position[0] + 's in NBA 2K League Season 6')
        st.pyplot(fig)

    if player2:
        player_name = player2[0]
        selected_player_row = top_point_guards[top_point_guards['Player'] == player_name]

        # Calculate percentile ranks for the selected player
        player_data = selected_player_row[numeric_columns]
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
        ax.plot(angles, percentile_ranks_avg + [percentile_ranks_avg[0]], linewidth=2, label=f'Avg {position[0]}')
        plt.xticks(angles[:-1], numeric_columns, color='white', size=8)
        plt.yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        plt.title(f'{player_name} vs. Avg ' + position[0]+ ' Percentile Comparison')
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.style.use('dark_background')
        st.subheader(player2[0]+' vs. League Average ' + position[0] + 's in NBA 2K League Season 6')
        st.pyplot(fig)

    if player1 and player2:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 9), subplot_kw={'polar': True})
        st.subheader(player1[0]+' vs. ' + player2[0] + ' side by side comparison at '+ position[0] + ' (Season 6)')
        # Plot for Player 1
        player_name1 = player1[0]
        selected_player_row1 = top_point_guards[top_point_guards['Player'] == player_name1]
        player_data1 = selected_player_row1[numeric_columns]
        percentile_ranks_player1 = [percentileofscore(league_data[column], player_data1[column]) for column in numeric_columns]
        percentile_ranks_player1 = [rank / 100 for rank in percentile_ranks_player1]  # Convert to floats
        ax1.plot(angles, percentile_ranks_player1 + [percentile_ranks_player1[0]], linewidth=2, label=player_name1)
        ax1.fill(angles, percentile_ranks_player1 + [percentile_ranks_player1[0]], alpha=0.25)
        ax1.set_xticks(angles[:-1])
        ax1.set_xticklabels(numeric_columns, color='white', size=8)
        ax1.set_yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        ax1.set_title(f'{player_name1} Percentile Comparison', color='white')
        
        # Plot for Player 2
        player_name2 = player2[0]
        selected_player_row2 = top_point_guards[top_point_guards['Player'] == player_name2]
        player_data2 = selected_player_row2[numeric_columns]
        percentile_ranks_player2 = [percentileofscore(league_data[column], player_data2[column]) for column in numeric_columns]
        percentile_ranks_player2 = [rank / 100 for rank in percentile_ranks_player2]  # Convert to floats
        ax2.plot(angles, percentile_ranks_player2 + [percentile_ranks_player2[0]], linewidth=2, label=player_name2)
        ax2.fill(angles, percentile_ranks_player2 + [percentile_ranks_player2[0]], alpha=0.25)
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(numeric_columns, color='white', size=8)
        ax2.set_yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        ax2.set_title(f'{player_name2} Percentile Comparison', color='white')
        
        # Final adjustments
        plt.subplots_adjust(wspace=0.4)
        plt.style.use('dark_background')
        st.pyplot(fig)
elif position [0] == 'SF':
    top_point_guards = all_data[all_data['Pos.'] == 'SF']
    if player1:
        player_name = player1[0]
        selected_player_row = top_point_guards[top_point_guards['Player'] == player_name]

        # Calculate percentile ranks for the selected player
        player_data = selected_player_row[numeric_columns]
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
        ax.plot(angles, percentile_ranks_avg + [percentile_ranks_avg[0]], linewidth=2, label=f'Avg {position[0]}')
        plt.xticks(angles[:-1], numeric_columns, color='white', size=8)
        plt.yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        plt.title(f'{player_name} vs. Avg {position[0]} Percentile Comparison')
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.style.use('dark_background')
        st.subheader(player1[0]+' vs. League Average ' + position[0] + 's in NBA 2K League Season 6')
        st.pyplot(fig)

    if player2:
        player_name = player2[0]
        selected_player_row = top_point_guards[top_point_guards['Player'] == player_name]

        # Calculate percentile ranks for the selected player
        player_data = selected_player_row[numeric_columns]
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
        ax.plot(angles, percentile_ranks_avg + [percentile_ranks_avg[0]], linewidth=2, label=f'Average {position[0]}')
        plt.xticks(angles[:-1], numeric_columns, color='white', size=8)
        plt.yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        plt.title(f'{player_name} vs. Avg ' + position[0]+ ' Percentile Comparison')
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.style.use('dark_background')
        st.subheader(player2[0]+' vs. League Average ' + position[0] + 's in NBA 2K League Season 6')
        st.pyplot(fig)

    if player1 and player2:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 9), subplot_kw={'polar': True})
        st.subheader(player1[0]+' vs. ' + player2[0] + ' side by side comparison at '+ position[0] + ' (Season 6)')
        # Plot for Player 1
        player_name1 = player1[0]
        selected_player_row1 = top_point_guards[top_point_guards['Player'] == player_name1]
        player_data1 = selected_player_row1[numeric_columns]
        percentile_ranks_player1 = [percentileofscore(league_data[column], player_data1[column]) for column in numeric_columns]
        percentile_ranks_player1 = [rank / 100 for rank in percentile_ranks_player1]  # Convert to floats
        ax1.plot(angles, percentile_ranks_player1 + [percentile_ranks_player1[0]], linewidth=2, label=player_name1)
        ax1.fill(angles, percentile_ranks_player1 + [percentile_ranks_player1[0]], alpha=0.25)
        ax1.set_xticks(angles[:-1])
        ax1.set_xticklabels(numeric_columns, color='white', size=8)
        ax1.set_yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        ax1.set_title(f'{player_name1} Percentile Comparison', color='white')
        
        # Plot for Player 2
        player_name2 = player2[0]
        selected_player_row2 = top_point_guards[top_point_guards['Player'] == player_name2]
        player_data2 = selected_player_row2[numeric_columns]
        percentile_ranks_player2 = [percentileofscore(league_data[column], player_data2[column]) for column in numeric_columns]
        percentile_ranks_player2 = [rank / 100 for rank in percentile_ranks_player2]  # Convert to floats
        ax2.plot(angles, percentile_ranks_player2 + [percentile_ranks_player2[0]], linewidth=2, label=player_name2)
        ax2.fill(angles, percentile_ranks_player2 + [percentile_ranks_player2[0]], alpha=0.25)
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(numeric_columns, color='white', size=8)
        ax2.set_yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        ax2.set_title(f'{player_name2} Percentile Comparison', color='white')
        
        # Final adjustments
        plt.subplots_adjust(wspace=0.4)
        plt.style.use('dark_background')
        st.pyplot(fig)
elif position [0] == 'PF':
    top_point_guards = all_data[all_data['Pos.'] == 'PF']
    if player1:
        player_name = player1[0]
        selected_player_row = top_point_guards[top_point_guards['Player'] == player_name]

        # Calculate percentile ranks for the selected player
        player_data = selected_player_row[numeric_columns]
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
        ax.plot(angles, percentile_ranks_avg + [percentile_ranks_avg[0]], linewidth=2, label=f'Average {position[0]}')
        plt.xticks(angles[:-1], numeric_columns, color='white', size=8)
        plt.yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        plt.title(f'{player_name} vs. Avg {position[0]} Percentile Comparison')
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.style.use('dark_background')
        st.subheader(player1[0]+' vs. League Average ' + position[0] + 's in NBA 2K League Season 6')
        st.pyplot(fig)

    if player2:
        player_name = player2[0]
        selected_player_row = top_point_guards[top_point_guards['Player'] == player_name]

        # Calculate percentile ranks for the selected player
        player_data = selected_player_row[numeric_columns]
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
        ax.plot(angles, percentile_ranks_avg + [percentile_ranks_avg[0]], linewidth=2, label=f'Average {position[0]}')
        plt.xticks(angles[:-1], numeric_columns, color='white', size=8)
        plt.yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        plt.title(f'{player_name} vs. Avg ' + position[0]+ ' Percentile Comparison')
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.style.use('dark_background')
        st.subheader(player2[0]+' vs. League Average ' + position[0] + 's in NBA 2K League Season 6')
        st.pyplot(fig)

    if player1 and player2:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 9), subplot_kw={'polar': True})
        st.subheader(player1[0]+' vs. ' + player2[0] + ' side by side comparison at '+ position[0] + ' (Season 6)')
        # Plot for Player 1
        player_name1 = player1[0]
        selected_player_row1 = top_point_guards[top_point_guards['Player'] == player_name1]
        player_data1 = selected_player_row1[numeric_columns]
        percentile_ranks_player1 = [percentileofscore(league_data[column], player_data1[column]) for column in numeric_columns]
        percentile_ranks_player1 = [rank / 100 for rank in percentile_ranks_player1]  # Convert to floats
        ax1.plot(angles, percentile_ranks_player1 + [percentile_ranks_player1[0]], linewidth=2, label=player_name1)
        ax1.fill(angles, percentile_ranks_player1 + [percentile_ranks_player1[0]], alpha=0.25)
        ax1.set_xticks(angles[:-1])
        ax1.set_xticklabels(numeric_columns, color='white', size=8)
        ax1.set_yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        ax1.set_title(f'{player_name1} Percentile Comparison', color='white')
        
        # Plot for Player 2
        player_name2 = player2[0]
        selected_player_row2 = top_point_guards[top_point_guards['Player'] == player_name2]
        player_data2 = selected_player_row2[numeric_columns]
        percentile_ranks_player2 = [percentileofscore(league_data[column], player_data2[column]) for column in numeric_columns]
        percentile_ranks_player2 = [rank / 100 for rank in percentile_ranks_player2]  # Convert to floats
        ax2.plot(angles, percentile_ranks_player2 + [percentile_ranks_player2[0]], linewidth=2, label=player_name2)
        ax2.fill(angles, percentile_ranks_player2 + [percentile_ranks_player2[0]], alpha=0.25)
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(numeric_columns, color='white', size=8)
        ax2.set_yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        ax2.set_title(f'{player_name2} Percentile Comparison', color='white')
        
        # Final adjustments
        plt.subplots_adjust(wspace=0.4)
        plt.style.use('dark_background')
        st.pyplot(fig)
elif position[0] == 'C':
    top_point_guards = all_data[all_data['Pos.'] == 'C']
    if player1:
        player_name = player1[0]
        selected_player_row = top_point_guards[top_point_guards['Player'] == player_name]

        # Calculate percentile ranks for the selected player
        player_data = selected_player_row[numeric_columns]
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
        ax.plot(angles, percentile_ranks_avg + [percentile_ranks_avg[0]], linewidth=2, label=f'Avg {position[0]}')
        plt.xticks(angles[:-1], numeric_columns, color='white', size=8)
        plt.yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        plt.title(f'{player_name} vs. Avg {position[0]} Percentile Comparison')
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.style.use('dark_background')
        st.subheader(player1[0]+' vs. League Average ' + position[0] + 's in NBA 2K League Season 6')
        st.pyplot(fig)

    if player2:
        player_name = player2[0]
        selected_player_row = top_point_guards[top_point_guards['Player'] == player_name]

        # Calculate percentile ranks for the selected player
        player_data = selected_player_row[numeric_columns]
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
        ax.plot(angles, percentile_ranks_avg + [percentile_ranks_avg[0]], linewidth=2, label=f'Average {position[0]}')
        plt.xticks(angles[:-1], numeric_columns, color='white', size=8)
        plt.yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        plt.title(f'{player_name} vs. Avg ' + position[0]+ ' Percentile Comparison')
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.style.use('dark_background')
        st.subheader(player2[0]+' vs. League Average ' + position[0] + 's in NBA 2K League Season 6')
        st.pyplot(fig)

    if player1 and player2:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 9), subplot_kw={'polar': True})
        st.subheader(player1[0]+' vs. ' + player2[0] + ' side by side comparison at '+ position[0] + ' (Season 6)')
        # Plot for Player 1
        player_name1 = player1[0]
        selected_player_row1 = top_point_guards[top_point_guards['Player'] == player_name1]
        player_data1 = selected_player_row1[numeric_columns]
        percentile_ranks_player1 = [percentileofscore(league_data[column], player_data1[column]) for column in numeric_columns]
        percentile_ranks_player1 = [rank / 100 for rank in percentile_ranks_player1]  # Convert to floats
        ax1.plot(angles, percentile_ranks_player1 + [percentile_ranks_player1[0]], linewidth=2, label=player_name1)
        ax1.fill(angles, percentile_ranks_player1 + [percentile_ranks_player1[0]], alpha=0.25)
        ax1.set_xticks(angles[:-1])
        ax1.set_xticklabels(numeric_columns, color='white', size=8)
        ax1.set_yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        ax1.set_title(f'{player_name1} Percentile Comparison', color='white')
        
        # Plot for Player 2
        player_name2 = player2[0]
        selected_player_row2 = top_point_guards[top_point_guards['Player'] == player_name2]
        player_data2 = selected_player_row2[numeric_columns]
        percentile_ranks_player2 = [percentileofscore(league_data[column], player_data2[column]) for column in numeric_columns]
        percentile_ranks_player2 = [rank / 100 for rank in percentile_ranks_player2]  # Convert to floats
        ax2.plot(angles, percentile_ranks_player2 + [percentile_ranks_player2[0]], linewidth=2, label=player_name2)
        ax2.fill(angles, percentile_ranks_player2 + [percentile_ranks_player2[0]], alpha=0.25)
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(numeric_columns, color='white', size=8)
        ax2.set_yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        ax2.set_title(f'{player_name2} Percentile Comparison', color='white')
        
        # Final adjustments
        plt.subplots_adjust(wspace=0.4)
        plt.style.use('dark_background')
        st.pyplot(fig)
elif position[0] == 'C':
    top_point_guards = all_data[all_data['Pos.'] == 'C']
    if player1:
        player_name = player1[0]
        selected_player_row = top_point_guards[top_point_guards['Player'] == player_name]

        # Calculate percentile ranks for the selected player
        player_data = selected_player_row[numeric_columns]
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
        ax.plot(angles, percentile_ranks_avg + [percentile_ranks_avg[0]], linewidth=2, label=f'Avg {position[0]}')
        plt.xticks(angles[:-1], numeric_columns, color='white', size=8)
        plt.yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        plt.title(f'{player_name} vs. Avg {position[0]} Percentile Comparison')
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.style.use('dark_background')
        st.subheader(player1[0]+' vs. League Average ' + position[0] + 's in NBA 2K League Season 6')
        st.pyplot(fig)

    if player2:
        player_name = player2[0]
        selected_player_row = top_point_guards[top_point_guards['Player'] == player_name]

        # Calculate percentile ranks for the selected player
        player_data = selected_player_row[numeric_columns]
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
        ax.plot(angles, percentile_ranks_avg + [percentile_ranks_avg[0]], linewidth=2, label=f'Average {position[0]}')
        plt.xticks(angles[:-1], numeric_columns, color='white', size=8)
        plt.yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        plt.title(f'{player_name} vs. Avg ' + position[0]+ ' Percentile Comparison')
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.style.use('dark_background')
        st.subheader(player2[0]+' vs. League Average ' + position[0] + 's in NBA 2K League Season 6')
        st.pyplot(fig)

    if player1 and player2:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 9), subplot_kw={'polar': True})
        st.subheader(player1[0]+' vs. ' + player2[0] + ' side by side comparison at '+ position[0] + ' (Season 6)')
        # Plot for Player 1
        player_name1 = player1[0]
        selected_player_row1 = top_point_guards[top_point_guards['Player'] == player_name1]
        player_data1 = selected_player_row1[numeric_columns]
        percentile_ranks_player1 = [percentileofscore(league_data[column], player_data1[column]) for column in numeric_columns]
        percentile_ranks_player1 = [rank / 100 for rank in percentile_ranks_player1]  # Convert to floats
        ax1.plot(angles, percentile_ranks_player1 + [percentile_ranks_player1[0]], linewidth=2, label=player_name1)
        ax1.fill(angles, percentile_ranks_player1 + [percentile_ranks_player1[0]], alpha=0.25)
        ax1.set_xticks(angles[:-1])
        ax1.set_xticklabels(numeric_columns, color='white', size=8)
        ax1.set_yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        ax1.set_title(f'{player_name1} Percentile Comparison', color='white')
        
        # Plot for Player 2
        player_name2 = player2[0]
        selected_player_row2 = top_point_guards[top_point_guards['Player'] == player_name2]
        player_data2 = selected_player_row2[numeric_columns]
        percentile_ranks_player2 = [percentileofscore(league_data[column], player_data2[column]) for column in numeric_columns]
        percentile_ranks_player2 = [rank / 100 for rank in percentile_ranks_player2]  # Convert to floats
        ax2.plot(angles, percentile_ranks_player2 + [percentile_ranks_player2[0]], linewidth=2, label=player_name2)
        ax2.fill(angles, percentile_ranks_player2 + [percentile_ranks_player2[0]], alpha=0.25)
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(numeric_columns, color='white', size=8)
        ax2.set_yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        ax2.set_title(f'{player_name2} Percentile Comparison', color='white')
        
        # Final adjustments
        plt.subplots_adjust(wspace=0.4)
        plt.style.use('dark_background')
        st.pyplot(fig)
elif position[0] == 'PF/C':
    top_point_guards = all_data[all_data['Pos.'] == 'PF/C']
    if player1:
        player_name = player1[0]
        selected_player_row = top_point_guards[top_point_guards['Player'] == player_name]

        # Calculate percentile ranks for the selected player
        player_data = selected_player_row[numeric_columns]
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
        ax.plot(angles, percentile_ranks_avg + [percentile_ranks_avg[0]], linewidth=2, label=f'Avg {position[0]}')
        plt.xticks(angles[:-1], numeric_columns, color='white', size=8)
        plt.yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        plt.title(f'{player_name} vs. Avg {position[0]} Percentile Comparison')
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.style.use('dark_background')
        st.subheader(player1[0]+' vs. League Average ' + position[0] + 's in NBA 2K League Season 6')
        st.pyplot(fig)

    if player2:
        player_name = player2[0]
        selected_player_row = top_point_guards[top_point_guards['Player'] == player_name]

        # Calculate percentile ranks for the selected player
        player_data = selected_player_row[numeric_columns]
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
        ax.plot(angles, percentile_ranks_avg + [percentile_ranks_avg[0]], linewidth=2, label=f'Average {position[0]}')
        plt.xticks(angles[:-1], numeric_columns, color='white', size=8)
        plt.yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        plt.title(f'{player_name} vs. Avg ' + position[0]+ ' Percentile Comparison')
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.style.use('dark_background')
        st.subheader(player2[0]+' vs. League Average ' + position[0] + 's in NBA 2K League Season 6')
        st.pyplot(fig)

    if player1 and player2:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 9), subplot_kw={'polar': True})
        st.subheader(player1[0]+' vs. ' + player2[0] + ' side by side comparison at '+ position[0] + ' (Season 6)')
        # Plot for Player 1
        player_name1 = player1[0]
        selected_player_row1 = top_point_guards[top_point_guards['Player'] == player_name1]
        player_data1 = selected_player_row1[numeric_columns]
        percentile_ranks_player1 = [percentileofscore(league_data[column], player_data1[column]) for column in numeric_columns]
        percentile_ranks_player1 = [rank / 100 for rank in percentile_ranks_player1]  # Convert to floats
        ax1.plot(angles, percentile_ranks_player1 + [percentile_ranks_player1[0]], linewidth=2, label=player_name1)
        ax1.fill(angles, percentile_ranks_player1 + [percentile_ranks_player1[0]], alpha=0.25)
        ax1.set_xticks(angles[:-1])
        ax1.set_xticklabels(numeric_columns, color='white', size=8)
        ax1.set_yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        ax1.set_title(f'{player_name1} Percentile Comparison', color='white')
        
        # Plot for Player 2
        player_name2 = player2[0]
        selected_player_row2 = top_point_guards[top_point_guards['Player'] == player_name2]
        player_data2 = selected_player_row2[numeric_columns]
        percentile_ranks_player2 = [percentileofscore(league_data[column], player_data2[column]) for column in numeric_columns]
        percentile_ranks_player2 = [rank / 100 for rank in percentile_ranks_player2]  # Convert to floats
        ax2.plot(angles, percentile_ranks_player2 + [percentile_ranks_player2[0]], linewidth=2, label=player_name2)
        ax2.fill(angles, percentile_ranks_player2 + [percentile_ranks_player2[0]], alpha=0.25)
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(numeric_columns, color='white', size=8)
        ax2.set_yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        ax2.set_title(f'{player_name2} Percentile Comparison', color='white')
        
        # Final adjustments
        plt.subplots_adjust(wspace=0.4)
        plt.style.use('dark_background')
        st.pyplot(fig)
elif position[0] == 'SF/C':
    top_point_guards = all_data[all_data['Pos.'] == 'SF/C']
    if player1:
        player_name = player1[0]
        selected_player_row = top_point_guards[top_point_guards['Player'] == player_name]

        # Calculate percentile ranks for the selected player
        player_data = selected_player_row[numeric_columns]
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
        ax.plot(angles, percentile_ranks_avg + [percentile_ranks_avg[0]], linewidth=2, label=f'Avg {position[0]}')
        plt.xticks(angles[:-1], numeric_columns, color='white', size=8)
        plt.yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        plt.title(f'{player_name} vs. Avg {position[0]} Percentile Comparison')
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.style.use('dark_background')
        st.subheader(player1[0]+' vs. League Average ' + position[0] + 's in NBA 2K League Season 6')
        st.pyplot(fig)

    if player2:
        player_name = player2[0]
        selected_player_row = top_point_guards[top_point_guards['Player'] == player_name]

        # Calculate percentile ranks for the selected player
        player_data = selected_player_row[numeric_columns]
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
        ax.plot(angles, percentile_ranks_avg + [percentile_ranks_avg[0]], linewidth=2, label=f'Average {position[0]}')
        plt.xticks(angles[:-1], numeric_columns, color='white', size=8)
        plt.yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        plt.title(f'{player_name} vs. Avg ' + position[0]+ ' Percentile Comparison')
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.style.use('dark_background')
        st.subheader(player2[0]+' vs. League Average ' + position[0] + 's in NBA 2K League Season 6')
        st.pyplot(fig)

    if player1 and player2:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 9), subplot_kw={'polar': True})
        st.subheader(player1[0]+' vs. ' + player2[0] + ' side by side comparison at '+ position[0] + ' (Season 6)')
        # Plot for Player 1
        player_name1 = player1[0]
        selected_player_row1 = top_point_guards[top_point_guards['Player'] == player_name1]
        player_data1 = selected_player_row1[numeric_columns]
        percentile_ranks_player1 = [percentileofscore(league_data[column], player_data1[column]) for column in numeric_columns]
        percentile_ranks_player1 = [rank / 100 for rank in percentile_ranks_player1]  # Convert to floats
        ax1.plot(angles, percentile_ranks_player1 + [percentile_ranks_player1[0]], linewidth=2, label=player_name1)
        ax1.fill(angles, percentile_ranks_player1 + [percentile_ranks_player1[0]], alpha=0.25)
        ax1.set_xticks(angles[:-1])
        ax1.set_xticklabels(numeric_columns, color='white', size=8)
        ax1.set_yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        ax1.set_title(f'{player_name1} Percentile Comparison', color='white')
        
        # Plot for Player 2
        player_name2 = player2[0]
        selected_player_row2 = top_point_guards[top_point_guards['Player'] == player_name2]
        player_data2 = selected_player_row2[numeric_columns]
        percentile_ranks_player2 = [percentileofscore(league_data[column], player_data2[column]) for column in numeric_columns]
        percentile_ranks_player2 = [rank / 100 for rank in percentile_ranks_player2]  # Convert to floats
        ax2.plot(angles, percentile_ranks_player2 + [percentile_ranks_player2[0]], linewidth=2, label=player_name2)
        ax2.fill(angles, percentile_ranks_player2 + [percentile_ranks_player2[0]], alpha=0.25)
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(numeric_columns, color='white', size=8)
        ax2.set_yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        ax2.set_title(f'{player_name2} Percentile Comparison', color='white')
        
        # Final adjustments
        plt.subplots_adjust(wspace=0.4)
        plt.style.use('dark_background')
        st.pyplot(fig)
elif position [0] == 'SF/PF':
    top_point_guards = all_data[all_data['Pos.'] == 'SF/PF']
    if player1:
        player_name = player1[0]
        selected_player_row = top_point_guards[top_point_guards['Player'] == player_name]

        # Calculate percentile ranks for the selected player
        player_data = selected_player_row[numeric_columns]
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
        ax.plot(angles, percentile_ranks_avg + [percentile_ranks_avg[0]], linewidth=2, label=f'Avg {position[0]}')
        plt.xticks(angles[:-1], numeric_columns, color='white', size=8)
        plt.yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        plt.title(f'{player_name} vs. Avg {position[0]} Percentile Comparison')
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.style.use('dark_background')
        st.subheader(player1[0]+' vs. League Average ' + position[0] + 's in NBA 2K League Season 6')
        st.pyplot(fig)

    if player2:
        player_name = player2[0]
        selected_player_row = top_point_guards[top_point_guards['Player'] == player_name]

        # Calculate percentile ranks for the selected player
        player_data = selected_player_row[numeric_columns]
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
        ax.plot(angles, percentile_ranks_avg + [percentile_ranks_avg[0]], linewidth=2, label= f'Average {position[0]}')
        plt.xticks(angles[:-1], numeric_columns, color='white', size=8)
        plt.yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        plt.title(f'{player_name} vs. Avg ' + position[0]+ ' Percentile Comparison')
        plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.style.use('dark_background')
        st.subheader(player2[0]+' vs. League Average ' + position[0] + 's in NBA 2K League Season 6')
        st.pyplot(fig)

    if player1 and player2:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 9), subplot_kw={'polar': True})
        st.subheader(player1[0]+' vs. ' + player2[0] + ' side by side comparison at '+ position[0] + ' (Season 6)')
        # Plot for Player 1
        player_name1 = player1[0]
        selected_player_row1 = top_point_guards[top_point_guards['Player'] == player_name1]
        player_data1 = selected_player_row1[numeric_columns]
        percentile_ranks_player1 = [percentileofscore(league_data[column], player_data1[column]) for column in numeric_columns]
        percentile_ranks_player1 = [rank / 100 for rank in percentile_ranks_player1]  # Convert to floats
        ax1.plot(angles, percentile_ranks_player1 + [percentile_ranks_player1[0]], linewidth=2, label=player_name1)
        ax1.fill(angles, percentile_ranks_player1 + [percentile_ranks_player1[0]], alpha=0.25)
        ax1.set_xticks(angles[:-1])
        ax1.set_xticklabels(numeric_columns, color='white', size=8)
        ax1.set_yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        ax1.set_title(f'{player_name1} Percentile Comparison', color='white')
        
        # Plot for Player 2
        player_name2 = player2[0]
        selected_player_row2 = top_point_guards[top_point_guards['Player'] == player_name2]
        player_data2 = selected_player_row2[numeric_columns]
        percentile_ranks_player2 = [percentileofscore(league_data[column], player_data2[column]) for column in numeric_columns]
        percentile_ranks_player2 = [rank / 100 for rank in percentile_ranks_player2]  # Convert to floats
        ax2.plot(angles, percentile_ranks_player2 + [percentile_ranks_player2[0]], linewidth=2, label=player_name2)
        ax2.fill(angles, percentile_ranks_player2 + [percentile_ranks_player2[0]], alpha=0.25)
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(numeric_columns, color='white', size=8)
        ax2.set_yticks(np.linspace(0, 1, 5), ['0%', '25%', '50%', '75%', '100%'], color='white', size=7)
        ax2.set_title(f'{player_name2} Percentile Comparison', color='white')
        
        # Final adjustments
        plt.subplots_adjust(wspace=0.4)
        plt.style.use('dark_background')
        st.pyplot(fig)
