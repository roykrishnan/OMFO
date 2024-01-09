import streamlit as st 
import pandas as pd
from streamlit_extras.app_logo import add_logo

add_logo("images/liquid_logo.png", height = 65)

# Load the data
df = pd.read_csv('data/2023stats.csv', skiprows=1)
#side bar
st.sidebar.image("images/small_logo.png",caption="Developed and Maintained by Roy Krishnan")

# Calculate 'Efficiency' and preprocess columns
df['Eff'] = ((df['PTS'] + (df['DREB'] + df['OREB']) + df['AST'] + df['STL'] + df['BLK'] - (df['FGA'] - df['FGM']) - df['TOV']) / df['GP']).round(2)
df = df.drop("Person_id", axis='columns')
df['FG%'] = df['FG%'] * 100
df['FG3%'] = df['FG3%'] * 100
df['FT%'] = df['FT%'] * 100

# Streamlit setup
st.title(":bar_chart: Dashboard:")
st.markdown("##")

# Stats columns
name = df["Player"]
team = df['Team']
games_played =  df['GP']
fgm = df['FGM']
fga = df['FGA']
fg_percent = df['FG%']
fg3m = df['FG3M']
fg3a = df['FG3A']
fg3_percent = df['FG3%']
ftm = df['FTM']
fta = df['FTA']
ft_percent = df['FT%']
oreb = df['OREB']
dreb = df['DREB']
total_reb = (oreb + dreb)
ast = df['AST']
fouls = df['PF']
stl = df['STL']
tos = df['TOV']
blk = df['BLK']
pts = df['PTS']
pos = df["Pos."]
efficiency = df['Eff']

# Create a select box to choose between "Front Court" and "Back Court"
selection = st.selectbox("Select Position:", ["PG/SG/C", "SF/PF"])
selection1 = st.selectbox("Select Statistic:", ["Helio Grade", "Careless Index", "Trigger Score (2023 Finals: BETA)", "Floor Space Tendency (2023 Finals: BETA)"])

def triangle():
    # PG filter - create 
    eff_df_pg = df[['Player', "Pos.", "Eff"]]
    eff_df_pg = eff_df_pg[eff_df_pg['Pos.'] == 'PG']
    eff_df_pg.reset_index(drop=True, inplace=True)
    std_dev_pg = 3.55

    eff_max_pg = eff_df_pg['Eff'].max()
    S_pg = eff_max_pg
    A_pg = eff_max_pg - std_dev_pg
    B_pg = A_pg - std_dev_pg
    C_pg = B_pg - std_dev_pg
    D_pg = C_pg - std_dev_pg
    F_pg = D_pg - std_dev_pg

    for index, row in eff_df_pg.iterrows():
        eff = row['Eff']
        if eff > A_pg:
            eff_df_pg.at[index, 'Helio Score'] = 'A'
        elif eff > B_pg:
            eff_df_pg.at[index, 'Helio Score'] = 'B'
        elif eff > C_pg:
            eff_df_pg.at[index, 'Helio Score'] = 'C'
        elif eff > D_pg:
            eff_df_pg.at[index, 'Helio Score'] = "D"
        else:
            eff_df_pg.at[index, 'Helio Score'] = "F"

    # Creating displays and focus values: 
    left_column, middle_column, right_column = st.columns(3)

    with left_column:
        st.subheader('Offensive Impact (PG):')
        st.dataframe(eff_df_pg, hide_index=True, use_container_width=True)
        

    # Quantitative: Positional pages, Team Match Ups, Rotation %, Second Chance Points. 
    # Qualitative: Tendencies, Normal Shots v.s Fades. 

    # SG filter - create 
    eff_df_SG = df[['Player', "Pos.", "Eff"]]
    eff_df_SG = eff_df_SG[eff_df_SG['Pos.'] == 'SG']
    eff_df_SG.reset_index(drop=True, inplace=True)
    std_dev_SG = 2.94

    eff_max_SG = eff_df_SG['Eff'].max()
    S_SG = eff_max_SG
    A_SG = eff_max_SG - std_dev_SG
    B_SG = A_SG - std_dev_SG
    C_SG = B_SG - std_dev_SG
    D_SG = C_SG - std_dev_SG
    F_SG = D_SG - std_dev_SG

    for index, row in eff_df_SG.iterrows():
        eff = row['Eff']
        if eff > A_SG:
            eff_df_SG.at[index, 'Helio Score'] = 'A'
        elif eff > B_SG:
            eff_df_SG.at[index, 'Helio Score'] = 'B'
        elif eff > C_SG:
            eff_df_SG.at[index, 'Helio Score'] = 'C'
        elif eff > D_SG:
            eff_df_SG.at[index, 'Helio Score'] = 'D'
        else:
            eff_df_SG.at[index, 'Helio Score'] = 'F'

    with middle_column:
        st.subheader('Offensive Impact (SG):')
        st.dataframe(eff_df_SG, hide_index= True, use_container_width= True)

    # C filter - create 
    eff_df_C = df[['Player', "Pos.", "Eff"]]
    eff_df_C = eff_df_C[eff_df_C['Pos.'] == 'C']
    eff_df_C.reset_index(drop=True, inplace=True)
    std_dev_C = ((eff_df_C["Eff"].max()- eff_df_C["Eff"].min())/5)

    eff_max_C= eff_df_C['Eff'].max()
    S_C = eff_max_C
    A_C= eff_max_C - std_dev_C
    B_C= A_C - std_dev_C
    C_C = B_C - std_dev_C
    D_C = C_C - std_dev_C
    F_C = D_C - std_dev_C

    for index, row in eff_df_C.iterrows():
        eff = row['Eff']
        if eff > A_C:
            eff_df_C.at[index, 'Helio Score'] = 'A'
        elif eff > B_C:
            eff_df_C.at[index, 'Helio Score'] = 'B'
        elif eff > C_C:
            eff_df_C.at[index, 'Helio Score'] = 'C'
        elif eff > D_C:
            eff_df_C.at[index, 'Helio Score'] = 'D'
        else:
            eff_df_C.at[index, 'Helio Score'] = 'F'

    with right_column:
        st.subheader('Offensive Impact (C):')
        st.dataframe(eff_df_C, hide_index= True, use_container_width= True)

def corners():
    # PG filter - create 
    eff_df_pg = df[['Player', "Pos.", "Eff"]]
    eff_df_pg = eff_df_pg[eff_df_pg['Pos.'] == 'SF']
    eff_df_pg.reset_index(drop=True, inplace=True)
    std_dev_pg = ((eff_df_pg["Eff"].max()- eff_df_pg["Eff"].min())/5)

    eff_max_pg = eff_df_pg['Eff'].max()
    S_pg = eff_max_pg
    A_pg = eff_max_pg - std_dev_pg
    B_pg = A_pg - std_dev_pg
    C_pg = B_pg - std_dev_pg
    D_pg = C_pg - std_dev_pg
    F_pg = D_pg - std_dev_pg

    for index, row in eff_df_pg.iterrows():
        eff = row['Eff']
        if eff > A_pg:
            eff_df_pg.at[index, 'Helio Score'] = 'A'
        elif eff > B_pg:
            eff_df_pg.at[index, 'Helio Score'] = 'B'
        elif eff > C_pg:
            eff_df_pg.at[index, 'Helio Score'] = 'C'
        elif eff > D_pg:
            eff_df_pg.at[index, 'Helio Score'] = "D"
        else:
            eff_df_pg.at[index, 'Helio Score'] = "F"

    # Creating displays and focus values: 
    left_column, right_column = st.columns(2)

    with left_column:
        st.subheader('Offensive Impact (SF):')
        st.dataframe(eff_df_pg, hide_index=True, use_container_width=True)
        

    # Quantitative: Positional pages, Team Match Ups, Rotation %, Second Chance Points. 
    # Qualitative: Tendencies, Normal Shots v.s Fades. 

    # SG filter - create 
    eff_df_SG = df[['Player', "Pos.", "Eff"]]
    eff_df_SG = eff_df_SG[eff_df_SG['Pos.'] == 'PF']
    eff_df_SG.reset_index(drop=True, inplace=True)
    std_dev_SG = ((eff_df_SG["Eff"].max()- eff_df_SG["Eff"].min())/5)


    eff_max_SG = eff_df_SG['Eff'].max()
    S_SG = eff_max_SG
    A_SG = eff_max_SG - std_dev_SG
    B_SG = A_SG - std_dev_SG
    C_SG = B_SG - std_dev_SG
    D_SG = C_SG - std_dev_SG
    F_SG = D_SG - std_dev_SG

    for index, row in eff_df_SG.iterrows():
        eff = row['Eff']
        if eff > A_SG:
            eff_df_SG.at[index, 'Helio Score'] = 'A'
        elif eff > B_SG:
            eff_df_SG.at[index, 'Helio Score'] = 'B'
        elif eff > C_SG:
            eff_df_SG.at[index, 'Helio Score'] = 'C'
        elif eff > D_SG:
            eff_df_SG.at[index, 'Helio Score'] = 'D'
        else:
            eff_df_SG.at[index, 'Helio Score'] = 'F'

    with right_column:
        st.subheader('Offensive Impact (PF):')
        st.dataframe(eff_df_SG, hide_index= True, use_container_width= True)

def trigger():
    trigger_df = pd.read_csv('data/yeydata1.csv')
    st.dataframe(trigger_df, hide_index= True)

col1, col2, col3 = st.columns(3)
def careless_index():
    with col1:
        eff_df_pg = df[['Player', "Pos.", "AST", "TOV"]]
        eff_df_pg['Careless Index'] = (((eff_df_pg["AST"]) / (eff_df_pg["TOV"])).round(2))
        eff_df_pg.drop(columns=["AST", "TOV"], inplace=True)
        eff_df_pg = eff_df_pg[eff_df_pg['Pos.'] == 'PG']
        eff_df_pg.reset_index(drop=True, inplace=True)
        eff_df_pg = eff_df_pg.sort_values(by='Careless Index', ascending=True)  # Assign the sorted DataFrame back to eff_df_pg
        st.dataframe(eff_df_pg, hide_index= True)

    with col2:
        eff_df_pg = df[['Player', "Pos.", "AST", "TOV"]]
        eff_df_pg['Careless Index'] = (((eff_df_pg["AST"]) / (eff_df_pg["TOV"])).round(2))
        eff_df_pg = eff_df_pg[eff_df_pg['Pos.'] == 'SG']
        eff_df_pg.drop(columns=["AST", "TOV"], inplace=True)
        eff_df_pg.reset_index(drop=True, inplace=True)
        eff_df_pg = eff_df_pg.sort_values(by='Careless Index', ascending=True) 
        st.dataframe(eff_df_pg, hide_index= True)
    
    with col3: 
        eff_df_pg = df[['Player', "Pos.", "AST", "TOV"]]
        eff_df_pg['Careless Index'] = (((eff_df_pg["AST"]) / (eff_df_pg["TOV"])).round(2))
        eff_df_pg = eff_df_pg[eff_df_pg['Pos.'] == 'C']
        eff_df_pg.drop(columns=["AST", "TOV"], inplace=True)
        eff_df_pg.reset_index(drop=True, inplace=True)
        eff_df_pg = eff_df_pg.sort_values(by='Careless Index', ascending=True) 
        st.dataframe(eff_df_pg, hide_index= True)

def careless_index_corners():
    left_col, right_col = st.columns(2)
    with left_col:
        eff_df_pg = df[['Player', "Pos.", "AST", "TOV"]]
        eff_df_pg['Careless Index'] = (((eff_df_pg["AST"]) / (eff_df_pg["TOV"])).round(2))
        eff_df_pg = eff_df_pg[eff_df_pg['Pos.'] == 'SF']
        eff_df_pg.reset_index(drop=True, inplace=True)
        eff_df_pg = eff_df_pg.sort_values(by='Careless Index', ascending=True)  # Assign the sorted DataFrame back to eff_df_pg
        st.dataframe(eff_df_pg, hide_index= True)

    with right_col:
        eff_df_pg = df[['Player', "Pos.", "AST", "TOV"]]
        eff_df_pg['Careless Index'] = (((eff_df_pg["AST"]) / (eff_df_pg["TOV"])).round(2))
        eff_df_pg = eff_df_pg[eff_df_pg['Pos.'] == 'PF']
        eff_df_pg.reset_index(drop=True, inplace=True)
        eff_df_pg = eff_df_pg.sort_values(by='Careless Index', ascending=True) 
        st.dataframe(eff_df_pg, hide_index= True)
    

if selection == "PG/SG/C" and selection1 == "Helio Grade":
    triangle()
elif selection == "SF/PF" and selection1 == "Helio Grade":
    corners()
elif selection == "SF/PF" and selection1 == "Trigger Score (2023 Finals: BETA)":
    trigger()
elif selection == "PG/SG/C" and selection1 == "Trigger Score (2023 Finals: BETA)":
    st.write("Trigger Scores are not available for these positions.")
elif selection == "PG/SG/C" and selection1 == "Floor Space Tendency (2023 Finals: BETA)":
    yeydatadf = pd.read_csv("data/yeydata.csv")
    st.dataframe(yeydatadf, hide_index= True)
    st.write('Mashes: How often the Center attempts a Field Goal in the Paint')
    st.write('Mashes: How often the Center passes the ball out of the Paint')
    st.write(""" **Note:** Centers that mash well usually have teammates that give them the ball in beneficial situations as
             well as position themselves extremely well on the roll and/or the rebound to be able to be able to score more effectively.""")
elif selection == "PG/SG/C" and selection1 == "Careless Index":
    careless_index()
elif selection == "SF/PF" and selection1 == "Careless Index":
    careless_index_corners()


with st.expander("**What is Helio Grade?**"):
    st.write(""" Helio Score details how involved the player is in the production of his team's offense and shows his offensive impact. The higher the helio score the more important a player is to that team's offense.
             Therefore, player's with high Helio Scores should warrant extra attention in an effort to take them out of the game. """)
with st.expander("What is Trigger Score"):
    st.write("""Trigger Score examines a corner player's willingness to shoot. The higher their trigger score, the more willing and likely they 
            are to shoot the ball. This can be used in an effort to bait corner shooters into bad shots, but a careful balance is needed as high 
             Trigger Score players are often amaong the league's best shooters.""")
with st.expander("What is the Careless Index?"):
    st.write(""" Each pass should should be in an effort to lead to a better scoring opportunity, the players that turn the ball over consistently without
             being able to consistently deliver scoring opportunitied are ranked high on the Careless Index. """)
with st.expander("Understanding the Mash v. Pass Ratio"):
    st.write(""" Centers that show a tendency to attempt a field goal in the paint more than simply pass it back out show a more aggressive profile of wanting to score the ball.
             They can be regarded as 'non-reset Centers', players that have the ability to make a play on their own accord.""")