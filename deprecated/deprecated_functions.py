import pandas as pd
import requests
from IPython.core.display_functions import display
from bs4 import BeautifulSoup

from modules.functions import BadStatusCodeError, convert_dict, col_order, ids


def create_home_and_away_simple_dataframe(game_id: int,
                                          disp: bool = False) -> tuple:
    url = f'https://www.espn.com/mens-college-basketball/boxscore/_/gameId/{game_id}'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'lxml')

    if r.status_code != 200:
        raise BadStatusCodeError("Possibly invalid game_id.  Request did not return status code 200")

    # Isolate the home team, away team, and game date.  Away team is always first
    title_html_string = str(soup.find('title'))
    # Scan through the string and return the first non-alpha character index
    away_team = title_html_string[:[char.isdigit() for char in title_html_string].index(True)].replace(
        '<title data-react-helmet="true">', "").strip()
    home_team = " ".join(
        title_html_string.split("(")[0].replace('<title data-react-helmet="true">', "").replace(away_team, "").split()[
        1:])
    game_date = str(soup.find("title")).split("-")[-1].split("|")[0].strip()

    # Infer tables with Pandas
    dfs = pd.read_html(url)

    # Pandas pulls in a lot of dataframes
    # Filtering to only retrieve the entries we're interested in
    away_players, away_stats, home_players, home_stats = dfs[1:5]
    # Renaming the column in the home and away players dataframe to "player"
    away_players.columns, home_players.columns = ['Player'], ['Player']

    # Remove entries we don't need
    away_players = away_players.iloc[1:len(away_players), ]
    away_players = away_players.loc[away_players.Player != "bench"]

    # Remove entries we don't need
    home_players = home_players.iloc[1:len(home_players), ]
    home_players = home_players.loc[home_players.Player != "bench"]
    # Grabbing the last letter from the player column and isolating it into it's own column
    # This becomes the position (G,F,C)
    home_players['Position'] = [i[-1] for i in home_players.Player]
    away_players['Position'] = [i[-1] for i in away_players.Player]
    home_players['Player'] = [i[:-2].strip() for i in home_players.Player]
    away_players['Player'] = [i[:-2].strip() for i in away_players.Player]

    # Pandas doesn't recognize the first row as a header, so I'm manually assigning it to the stats dataframes
    away_stats.columns = away_stats.iloc[0, :].tolist()
    home_stats.columns = home_stats.iloc[0, :].tolist()

    # Removing column break headers
    if "FG" in home_stats.columns:

        home_stats = home_stats.loc[home_stats.FG != "FG"]
        away_stats = away_stats.loc[away_stats.FG != "FG"]

    elif "MIN" in home_stats.columns:

        home_stats = home_stats.loc[home_stats.MIN != "MIN"]
        away_stats = away_stats.loc[away_stats.MIN != "MIN"]

    else:
        print("Neither Column Exists")
        return home_stats, away_stats

    # Removing the last row as it's all null values
    home_stats = home_stats.iloc[:len(home_stats) - 1, ]
    away_stats = away_stats.iloc[:len(away_stats) - 1, ]

    # Merge the players and stats together
    home_df = home_players.join(home_stats).iloc[:-1].fillna("")
    away_df = away_players.join(away_stats).iloc[:-1].fillna("")

    home_df = clean_dataframe(home_df)
    away_df = clean_dataframe(away_df)

    # Create outer index
    away_df = pd.concat({away_team: away_df})
    home_df = pd.concat({home_team: home_df})

    # Set the Team PTS/FGA to zero
    home_df.loc[home_df.Player == "Team", 'PTS/FGA'] = int(0)
    away_df.loc[away_df.Player == "Team", 'PTS/FGA'] = int(0)

    if disp:
        display(away_df, home_df)
        return

    return home_df, away_df


def clean_dataframe(input_df: pd.DataFrame) -> pd.DataFrame:
    # Creating a copy of the DataFrame and adding the stats which I track
    df = input_df.copy()
    df['FGM'] = [i[0] for i in df.FG.str.split('-')]
    df['FGA'] = [i[1] for i in df.FG.str.split('-')]
    df['3PM'] = [i[0] for i in df['3PT'].str.split('-')]
    df['3PA'] = [i[1] for i in df['3PT'].str.split('-')]
    df['FTM'] = [i[0] for i in df.FT.str.split('-')]
    df['FTA'] = [i[1] for i in df.FT.str.split('-')]

    # Filling empty minutes with zeroes.  They show up in different data formats
    # if type(df.MIN[0]) == str:
    # df.MIN = 0

    # Converting datatypes before calculations
    df = df.astype(convert_dict)
    df['PTS/FGA'] = round((df.PTS / df.FGA), 2).fillna(0)
    # Adding a summary row
    df = df.append(df.sum(numeric_only=True), ignore_index=True)

    # Manually creating a new row
    # Assigning 'team' to the player and "" to the position.  This is where the aggregates will live
    last_row = len(df) - 1
    df = df[col_order]
    df.iloc[last_row, 0] = 'Team'
    df.iloc[last_row, 17] = ""

    # Converting to integer where possible
    for col in df.columns:

        if col != "PTS/FGA":

            try:
                df[col] = df[col].astype(int)
            except ValueError as e:
                continue

    # Every now and again, I'm left with residual NaNs, filling those
    df = df.fillna("")

    return df


def get_schedule(team):
    current_season = '2022-23'
    url = "https://www.espn.com/mens-college-basketball/team/schedule/_/id/"

    if team not in ids.team.unique().tolist():
        raise ValueError("Invalid Team Name")

    team_link = ids[ids.team == team].link.item()
    team_id = str(ids[ids.team == team].id.item())
    url = url + team_id + "/" + team_link

    # Initial Get Request and splitting the raw HTML by gameId
    r = requests.get(url).text
    test = r.split('gameId')

    # Cleaning and organizing resulting dataframe
    dfs = pd.read_html(url)
    df = dfs[0]
    df.columns = df.iloc[1, :].tolist()
    df = df.iloc[2:, [0, 1]]
    df = df[df.DATE != 'DATE']
    df['GAME_ID'] = [test[i][1:10] for i in range(1, len(df) + 1)]
    df.GAME_ID = df.GAME_ID.astype(int)
    df.OPPONENT = df.OPPONENT.str.replace("*", "")
    df.OPPONENT = df.OPPONENT.str.replace("\d", "")
    df.OPPONENT = df.OPPONENT.str.replace('vs', '')

    return df
