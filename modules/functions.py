import pandas as pd

# Global Variables
ids = pd.read_csv('Adjusting_Basketball_Stats/modules/ids.csv')


class BadStatusCodeError(Exception):
    pass


convert_dict = {'OREB': int,
                'DREB': int,
                'REB': int,
                'AST': int,
                'STL': int,
                'BLK': int,
                'TO': int,
                'PF': int,
                'PTS': int,
                'FGM': int,
                'FGA': int,
                '3PM': int,
                '3PA': int,
                'FTM': int,
                'FTA': int}

col_order = ['Player',
             'PTS',
             'FGM',
             'FGA',
             '3PM',
             '3PA',
             'FTM',
             'FTA',
             'OREB',
             'DREB',
             'REB',
             'AST',
             'STL',
             'BLK',
             'TO',
             'PF',
             'PTS/FGA',
             'Position']


# Functions

def calculate_possessions(fga, orebs, tos, fta):
    value = (fga - orebs) + tos + (0.475 * fta)
    return value


# Simple function to get a team's schedule for the season

