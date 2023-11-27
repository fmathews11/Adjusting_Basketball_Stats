import pandas as pd


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
                 player_advanced: pd.DataFrame) -> None:

        # Removed "Unnamed" columns and add in team names
        self.player_info = _remove_unnamed_columns(player_info).assign(team=team_name.upper())
        self.player_per_game_simple = _remove_unnamed_columns(player_per_game_simple).assign(team=team_name.upper())
        self.player_totals = _remove_unnamed_columns(player_totals).assign(team=team_name.upper())
        self.player_per_100_possessions = _remove_unnamed_columns(player_totals).assign(team=team_name.upper())
        self.player_per_100_possessions = _remove_unnamed_columns(player_per_100_possessions).assign(team=team_name.upper())
        self.player_advanced = _remove_unnamed_columns(player_advanced).assign(team=team_name.upper())

    def to_dict(self) -> dict[str: pd.DataFrame]:
        """Convert each DataFrame to a dictionary and return a dictionary of dictionaries"""

        return {key: val.to_dict(orient='records') for key, val in self.__dict__.items() if key != 'team_name'}
