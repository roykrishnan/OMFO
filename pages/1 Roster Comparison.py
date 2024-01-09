import streamlit as st 
import pandas as pd 
from streamlit_extras.app_logo import add_logo
import numpy as np 
import plotly_express as px

df = pd.read_csv('data/2023stats.csv', skiprows=1)
df['Eff'] = ((df['PTS'] + (df ['DREB'] + df['OREB']) + df['AST'] + df['STL'] + df['BLK'] - (df['FGA'] - df['FGM']) - df['TOV']) / df['GP']).round(2)
df = df.drop("Person_id", axis= 'columns')
df['FG%'] = df['FG%'] * 100
df['FG3%'] = df['FG3%'] * 100
df['FT%'] = df['FT%'] * 100

st.set_page_config(page_title= "One Man Front Office: 2K League Web App", page_icon = ":bar_chart:", layout= "wide")
#Use the app_logo function to display the logo
add_logo("images/liquid_logo.png", height = 75)
st.dataframe(df, hide_index= True)

#side bar
st.sidebar.image("images/small_logo.png", caption="Developed and Maintained by Roy Krishnan")
#Side Bar 
st.sidebar.header("Please Filter Here: ")

st.write('**Select team from sidebar to display:** ')
position = st.sidebar.multiselect(
    "Select Position: ",
    options=df["Pos."].unique(),
    default = df["Pos."].unique()
    )

team_name = st.sidebar.multiselect(
    "Select Team: ",
    options=df["Team"].unique(),
)

df_selection = df.query(
      "`Pos.` == @position and Team == @team_name")

st.dataframe(df_selection, hide_index= True, use_container_width = True)

#Create Team Report: 
if team_name:
        columns_to_chart = ['PTS', 'FG3M', 'AST', 'STL', 'TOV', 'FG%', 'OREB', 'DREB', 'BLK', 'Eff']
        with st.container():
            tab_titles = [f"{column} Chart" for column in columns_to_chart]
            tabs = st.tabs(tab_titles)
            
            for tab, column in zip(tabs, columns_to_chart):
                with tab:
                    st.write(f"{team_name[0]} {column} Comparison")
                    st.bar_chart(df_selection[['Player', column]].set_index('Player'), color= ['#FF0800'])
else:
    pass