import streamlit as st 
from streamlit_extras.app_logo import add_logo
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
add_logo("images/liquid_logo.png", height = 65)

df = pd.read_csv('data/2023stats.csv', skiprows=1)
df = df.drop("Person_id", axis= 'columns')
df['FG%'] = df['FG%'] * 100
df['FG3%'] = df['FG3%'] * 100
df['FT%'] = df['FT%'] * 100

#logo
st.sidebar.image("images/small_logo.png",caption="Developed and Maintained by Roy Krishnan")
#Side Bar 
st.sidebar.header("Please Filter Here: ")

team1 = st.sidebar.multiselect(
    "Select Team 1: ",
    default= "76ers GC",
    options=df["Team"].unique(),
    max_selections= 1,
    key="team1"
)

team2 = st.sidebar.multiselect(
    "Select Team 2: ",
    options=df["Team"].unique(),
    default= "Raptors Uprising GC",
    max_selections= 1,
    key="team2" 
)

if not team1 or not team2:
    st.write('Please select two teams to display')

# Calculate the sum for numeric columns and the mean for percentage columns
numeric_columns = ['GP', 'Min', 'FGM', 'FGA', 'FG3M', 'FG3A', 'FTM', 'FTA', 'OREB', 'DREB', 'REB', 'AST', 'PF', 'STL', 'TOV', 'BLK', 'PTS']
percentage_columns = ['FG%', 'FG3%', 'FT%']

if team1:
    total1 = df[df["Team"].isin(team1)] 
    total_row1 = {
        "Player": 'Total',
        'Team': team1,
        'Pos': '',
    }

    for col in numeric_columns:
        total_row1[col] = total1[col].sum()

    for col in percentage_columns:
        total_row1[col] = total1[col].mean()

    # Display the total row in a table
    display = (pd.DataFrame(total_row1, index=[0]))
    st.dataframe(display,hide_index= True, use_container_width= True)

df_matchup = df.query(
      "Team == @team1")

st.dataframe(df_matchup, hide_index= True, use_container_width = True)

df_matchup2 = df.query(
      "Team == @team2")

st.dataframe(df_matchup2, hide_index=True, use_container_width = True)

if team2: 
    total2 = df[df["Team"].isin(team2)]

    total_row2 = {
        "Player": 'Total',
        'Team': team2,
        'Pos': '',
    }

    for col in numeric_columns:
        total_row2[col] = total2[col].sum()

    for col in percentage_columns:
        total_row2[col] = total2[col].mean()

    # Display the total row in a table
    display2 = (pd.DataFrame(total_row2, index=[0]))
    st.dataframe(display2,hide_index= True, use_container_width= True)


# Making Team Funnel Reports that compare players (eg. Seem v. DJ...)
if team1 and team2:
    vis_stat = st.selectbox('Select statistic to visualize', 
                            ('PPG', 'FG3%', 'FG3A/G','AST/G', 'STL/G', 'TOV/G', 'FG%', 'OREB/G', 'DREB/G', 'BLK'))
    merged_df = pd.concat([df_matchup, df_matchup2], ignore_index=True)
    
    merged_df['PPG'] = merged_df['PTS'] / merged_df['GP'].round(2)
    merged_df['FG3%'] = (merged_df['FG3M'] / merged_df['FG3A']*100).round(2)
    merged_df['FG3A/G'] = merged_df['FG3A'] / merged_df['GP'].round(2)
    merged_df['AST/G'] = merged_df['AST'] / merged_df['GP'].round(2)
    merged_df['OREB/G'] = merged_df['OREB'] / merged_df['GP'].round(2)
    merged_df['DREB/G'] = merged_df['DREB'] / merged_df['GP'].round(2)
    merged_df['BLK/G'] = merged_df['BLK'] / merged_df['GP'].round(2)
    merged_df['STL/G'] = merged_df['STL'] / merged_df['GP'].round(2)
    merged_df['TOV/G'] = merged_df['TOV'] / merged_df['GP'].round(2)

    # Define the order of positions for the chart
    position_order = ['C', 'PF', 'SF', 'SG', 'PG']
    position_order.reverse()
    top_players_by_position = merged_df.groupby('Pos.').apply(lambda x: x.nlargest(2, vis_stat)).reset_index(drop=True)


    # Define new colors for the bars as requested
    red_black_colors = ['red', 'black'] * 3

    # Create a new figure for the horizontal stacked bar chart
    fig, ax = plt.subplots(figsize=(12, 7))

    # Determine the total width for each position to center the bars
    max_width = top_players_by_position.groupby('Pos.')[vis_stat].sum().max()

    # Loop over the positions and plot the bars
    for i, position in enumerate(position_order):
        # Filter the data for the current position
        position_data = top_players_by_position[top_players_by_position['Pos.'] == position]

        # Calculate the starting point for each bar to center them
        total_width = position_data[vis_stat].sum()
        start = (max_width - total_width) / 2

        # Plot the bars for each player
        for j, (player, fg) in enumerate(zip(position_data['Player'], position_data[vis_stat])):
            color = red_black_colors[j % 2]  # Alternate between red and black
            ax.barh(i, fg, left=start, color=color, edgecolor='white')
            start += fg

            # Add the player names and FG% as text labels inside the bars
            text_color = 'white' if color == 'black' else 'black'
            ax.text(start - fg/2, i, f"{player} ({fg:.1f})", ha='center', va='center', color=text_color, fontsize=10)

    # Set y-ticks to position names
    ax.set_yticks(range(len(position_order)))
    ax.set_yticklabels(position_order)

    # Set title
    ax.set_title(f' {team1[0]} vs. {team2[0]} {vis_stat} matchup comparison')

    # Invert the y-axis to have the center at the top
    ax.invert_yaxis()

    # Remove X axis
    ax.xaxis.set_visible(False)

    # Layout adjustment for Streamlit
    plt.tight_layout()

    # Display the plot in Streamlit
    st.pyplot(fig)

