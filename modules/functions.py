import pandas as pd,numpy as np, warnings,seaborn as sns, matplotlib.pyplot as plt, requests
from bs4 import BeautifulSoup
import sys 
import warnings
import time
import os
sys.path.insert(0,"..")
#warnings.filterwarnings("ignore")

#current_directory = os.getcwd()
#sys.path.append(f"{current_directory}\Adjustihg_Basketball_Stats")

#from csvs.load_ids_csv import load_id_csv



#ids = load_id_csv()


def calculate_possessions(fga,orebs,tos,fta):
    value = (fga-orebs) + tos + (0.475*fta)
    return value

# Simple function to get a team's schedule for the season
def get_schedule(team):

  current_season = '2022-23'
  url = "https://www.espn.com/mens-college-basketball/team/schedule/_/id/"

  if team not in ids.team.unique().tolist():
    raise ValueError("Invalid Team Name")

  team_link = ids[ids.team == team].link.item()
  team_id = str(ids[ids.team == team].id.item())
  url = url + team_id + "/" + team_link


 # Initial Get Request and splliting the raw HTML by gameId 
  r = requests.get(url).text
  test = r.split('gameId')

  # Cleaning and organizing resulting dataframe
  dfs = pd.read_html(url)
  df= dfs[0]
  df.columns = df.iloc[1,:].tolist()
  df = df.iloc[2:,[0,1]]
  df = df[df.DATE != 'DATE']
  df['GAME_ID'] = [test[i][1:10] for i in range(1,len(df)+1)]
  df.OPPONENT = df.OPPONENT.str.replace("*","")
  df.OPPONENT = df.OPPONENT.str.replace("\d","")
  df.OPPONENT = df.OPPONENT.str.replace('vs','')
  
  return df


if __name__ == "__main__":
    #print(get_schedule("Purdue"))
    #print("hello")
    current_directory = os.getcwd()
    print(current_directory)
    print('\n')
    for i in sys.path:
       print(i)
    print('\n')
    df = pd.read_csv('csvs/ids.csv')
    print(df)


