import pandas as pd
from typing import Optional
from sklearn.linear_model import Ridge
import numpy as np


def _remove_unnamed_columns(input_dataframe: pd.DataFrame) -> pd.DataFrame:
    """Returns a copy of a dataframe with all columns removed which begin with "UNNAMED"""
    return input_dataframe[[column for column in input_dataframe if not column.startswith("Unnamed")]].copy()


class TeamPlayerDataframeHub:
    """Simple dataclass to temporarily house various dataframes of team information"""

    def __init__(self,
                 team_name: str,
                 player_info: pd.DataFrame,
                 player_per_game_simple: pd.DataFrame,
                 player_totals: pd.DataFrame,
                 player_per_100_possessions: pd.DataFrame,
                 player_advanced: pd.DataFrame,
                 player_per_game_simple_conf: Optional[pd.DataFrame] = None,
                 player_advanced_conf: Optional[pd.DataFrame] = None,
                 player_totals_conf: Optional[pd.DataFrame] = None,
                 player_per_100_possessions_conf: Optional[pd.DataFrame] = None) -> None:
        # Removed "Unnamed" columns and add in team names
        self.player_info = _remove_unnamed_columns(player_info).assign(team=team_name.upper())
        self.player_per_game_simple = _remove_unnamed_columns(player_per_game_simple) \
            .assign(team=team_name.upper())

        self.player_totals = _remove_unnamed_columns(player_totals).assign(team=team_name.upper())
        self.player_per_100_possessions = _remove_unnamed_columns(player_per_100_possessions) \
            .assign(team=team_name.upper())
        self.player_advanced = _remove_unnamed_columns(player_advanced).assign(team=team_name.upper())

        # Ternary assignment
        self.player_per_game_simple_conf = _remove_unnamed_columns(player_per_game_simple_conf) \
            .assign(team=team_name.upper()) if player_per_100_possessions_conf is not None else None

        self.player_totals_conf = _remove_unnamed_columns(player_totals_conf).assign(
            team=team_name.upper()) if player_per_100_possessions_conf is not None else None

        self.player_per_100_possessions_conf = _remove_unnamed_columns(player_per_100_possessions_conf) \
            .assign(team=team_name.upper()) if player_per_100_possessions_conf is not None else None

        self.player_advanced_conf = _remove_unnamed_columns(player_advanced_conf).assign(
            team=team_name.upper()) if player_per_100_possessions_conf is not None else None

    def to_dict(self) -> dict[str: pd.DataFrame]:
        """Convert each DataFrame to a dictionary and return a dictionary of dictionaries"""

        return {key: val.to_dict(orient='records')
                for key, val in self.__dict__.items()
                if (key != 'team_name' and val is not None)}


class RegressionHub:

    def __init__(self,
                 ortg_regression: Ridge,
                 drtg_regression: Ridge,
                 pace_regression: Ridge,
                 regression_dict: dict[str, dict]) -> None:

        self.ortg_regression = ortg_regression
        self.drtg_regression = drtg_regression
        self.pace_regression = pace_regression
        self.regression_dict = regression_dict


class Team:

    def __init__(self,
                 name: str,
                 expected_offensive_rating: float) -> None:
        self.name = name
        self.expected_offensive_rating = expected_offensive_rating


class Game:

    def __init__(self,
                 team_1: Team,
                 team_2: Team,
                 expected_pace: float) -> None:
        self.team_1 = team_1
        self.team_2 = team_2
        self.expected_pace = expected_pace

    def play(self,
             return_score: bool = False):
        team_1_or = np.random.uniform(self.team_1.expected_offensive_rating * 0.85,
                                      self.team_1.expected_offensive_rating * 1.15)
        team_2_or = np.random.uniform(self.team_2.expected_offensive_rating * 0.85,
                                      self.team_2.expected_offensive_rating * 1.15)

        if not return_score:
            return self.team_1.name if team_1_or > team_2_or else self.team_2.name

        return self.team_1.name if team_1_or > team_2_or else self.team_2.name, round(
            team_1_or / 100 * self.expected_pace), round(team_2_or / 100 * self.expected_pace)