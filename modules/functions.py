import pandas as pd
from modules import constants


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

# Create a base dictionary which we'll populate iteratively
_base_regression_row_dict = {f"TM_{tm_id}": 0
                             for tm_id in set(constants.TEAM_NAME_ID_DICT.values())
                             if tm_id not in constants.NON_D1_IDs}

_base_regression_row_dict.update(
    {f"OPP_{tm_id}": 0
     for tm_id in set(constants.TEAM_NAME_ID_DICT.values())
     if tm_id not in constants.NON_D1_IDs})

# Invert the team id -> team name dictionary
team_id_name_dict = {v: k for k, v in constants.TEAM_NAME_ID_DICT.items()}


# Functions

def _calculate_possessions(fga, orebs, tos, fta):
    return (fga - orebs) + tos + (0.44 * fta)


def _preprocess_raw_box_scores_for_regression(input_dataframe: pd.DataFrame) -> pd.DataFrame:
    """
     - Parameters:
        input_dataframe - A dataframe created as a result of running `Daily_Team_Game_Log_Data_Pull.py`
     - Returns:
        A Dataframe with numeric data types where appropriate and filtered to only include games where division 1
        teams played division 1 opponents
    """
    # Copy the input DataFrame so as not to alter the original data
    df = input_dataframe.copy()
    # Map names of teams using the dictionary in the `constants.py` module
    df['team_id'] = df.team_name.map(constants.TEAM_NAME_ID_DICT)
    df['opp_id'] = df.opp_name.map(constants.TEAM_NAME_ID_DICT)
    # We only want games where D1 teams play D1 teams
    df = df.loc[~df.opp_id.isin(constants.NON_D1_IDs)].copy()
    df = df.loc[~df.team_id.isin(constants.NON_D1_IDs)].reset_index(drop=True).copy()
    # Assign a UI
    df['ui'] = df.team_name.str.cat(
                                    [df.opp_name,
                                     df.home.astype(str),
                                     df.date.astype(str)], sep="_") \
        .map(lambda x: "_".join(x.split(" ")))

    # Coerce appropriate columns to numeric data types
    for col in df.columns.tolist():
        try:
            df[col] = pd.to_numeric(df[col])
        except ValueError:
            continue

    # Assertions to alert if a Non-D1 school sneaks its way back in
    assert df.opp_id.nunique() == 362, f"The number of opponent IDS is {df.opp_id.nunique()}"
    assert df.team_id.nunique() == 362, f"The number of team IDS is {df.team_id.nunique()}"
    assert len(set(df.team_id.unique().tolist() + df.opp_id.unique().tolist())) == 362
    return df


def add_calculated_metrics_to_preprocessed_dataframe(input_dataframe: pd.DataFrame) -> pd.DataFrame:
    """
     - Parameters:
        input_dataframe: A dataframe created as a result of running `_preprocess_raw_box_scores_for_regression()`
     - Returns:
        A modified dataframe with possessions, offensive/defensive ratings, net rating, and turnover percentages
        calculated
    """
    df = input_dataframe.copy()
    df = _preprocess_raw_box_scores_for_regression(df)
    # Remove \xa0 from strings
    df.wl = df.wl.map(lambda x: x.replace(u"\xa0", u" "))
    # Isolate number of OTs
    df['ot'] = df.wl.map(lambda x: int(x.split("(")[1].split(" ")[0]) if len(x.split("(")) > 1 else 0)
    # Calculate total minutes played
    df['game_minutes'] = df.ot.map(lambda x: 40 if x == 0 else 40 + (5 * x))
    # Calculate possessions per minute and adjusting per 40 to account for games with overtime(s)
    df['possessions'] = df.apply(lambda x: _calculate_possessions(x.fga, x.orb, x.tov, x.fta), axis=1)
    df['opp_possessions'] = df.apply(lambda x: _calculate_possessions(x.opp_fga, x.opp_orb, x.opp_tov, x.opp_fta),
                                     axis=1)
    df['poss_per_minute'] = df.possessions / df.game_minutes
    df['poss_per_40'] = df.poss_per_minute * 40
    # Turnover pct, ORTG and DRTG
    df['to_pct'] = df.tov / df.possessions * 100
    df['opp_to_pct'] = df.opp_tov / df.opp_possessions * 100
    df['ortg'] = df.apply(lambda x: 100 * (x.score / x.possessions), axis=1)
    df['drtg'] = df.apply(lambda x: 100 * (x.opp_score / x.opp_possessions), axis=1)
    df['net_rtg'] = df.apply(lambda x: x.ortg - x.drtg, axis=1)
    return df


def convert_box_score_dataframe_to_regression_format(input_dataframe: pd.DataFrame) -> pd.DataFrame:
    """
        - Parameters:
           input_dataframe: A dataframe created as a result of running
           `Daily_Team_Game_Log_Data_Pull.py`
        - Returns:
           A modified dataframe with teams/opponents represented as dummy variables and the calculated fields
           joined on the right side
       """
    df = input_dataframe.copy()

    # Instantiate an output dictionary that we'll
    output_dict = {}
    # Iterate through games, populating the necessary information
    for meaningless_index_value, sub_dict in df.to_dict(orient='index').items():
        output_dict[meaningless_index_value] = _base_regression_row_dict.copy()
        team_id = sub_dict['team_id']
        opp_id = sub_dict['opp_id']
        output_dict[meaningless_index_value]["home"] = sub_dict['home']
        output_dict[meaningless_index_value][f"TM_{team_id}"] = 1
        output_dict[meaningless_index_value][f"OPP_{opp_id}"] = 1
        output_dict[meaningless_index_value]['ortg'] = sub_dict['ortg']
        output_dict[meaningless_index_value]['drtg'] = sub_dict['drtg']
        # Using the "per-40" number so values aren't inflated due to games with overtime periods
        output_dict[meaningless_index_value]['pace'] = sub_dict['poss_per_40']
        output_dict[meaningless_index_value]['to_pct'] = sub_dict['to_pct']
        output_dict[meaningless_index_value]['opp_to_pct'] = sub_dict['opp_to_pct']
        output_dict[meaningless_index_value]['game_date'] = sub_dict['date']
        output_dict[meaningless_index_value]['ui'] = sub_dict['ui']

    # Convert the output dictionary to a dataframe
    reg_df = pd.DataFrame(output_dict).transpose()
    # Coerce binary fields to integer data types
    for col in [i for i in reg_df.columns if (i.startswith("TM") or i.startswith("OPP"))]:
        reg_df[col] = reg_df[col].astype(int)
    return reg_df


