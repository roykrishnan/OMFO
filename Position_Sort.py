#Position Sort for our Streamlit App
"""
In order to properly display our player stats we have to filter by position
"""
import pandas as pd

# Load the CSV file into a DataFrame, skipping the first row
df = pd.read_csv('2023stats.csv', skiprows=[0])

# Define positions and corresponding file names
positions = ['PG', 'SG', 'SF', 'PF', 'C']
output_files = ['PointGuards.csv', 'ShootingsGuards.csv', 'SmallForwards.csv', 'PowerForwards.csv', 'Centers.csv']

# Loop through each position and create a separate CSV file
for position, output_file in zip(positions, output_files):
    filtered_df = df[df['Pos.'] == position]
    filtered_df.to_csv(output_file, index=False)

print("CSV files created successfully.")
