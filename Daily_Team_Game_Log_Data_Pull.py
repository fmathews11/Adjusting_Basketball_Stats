import pandas as pd
import numpy as np
from tqdm import tqdm
import time
from modules.log import create_logger
from modules.constants import MASTER_COLUMN_NAMES
import json

SEASON = 2024

url_prefix = 'https://www.sports-reference.com'
logger = create_logger("StatusLogger", 'info')

with open('json_files/team_uis.json', 'r') as f:
    team_name_id_dict = json.load(f)


def main() -> None:
    logger.info("Populating box scores from games played")
    # Instantiate empty data frame
    master_df = pd.DataFrame()
    # Create an iteration counter
    counter = 0
    # Create a random number between 100 and 300.  This is where the loop will pause
    # To not overload the site
    stop_to_rest_point = np.random.randint(20, 100)

    # Iterate through the dictionary
    for team_name, team_ui in tqdm(team_name_id_dict.items()):

        url_suffix = f'/cbb/schools/{team_ui}/men/2024'
        full_url = f"{url_prefix}{url_suffix}-gamelogs.html"
        logger.debug(full_url)

        # If there are NO GAMES, move on
        try:
            temp_df = pd.read_html(full_url)[0]
        except ValueError as e:
            msg = str(e)
            if msg == "No tables found":
                logger.warning(f"Skipping {team_name} due to no data")
                logger.info(f"Skipped URL: {full_url}")
                continue
            raise

        # Surface-level data cleaning
        temp_df.columns = [col2 if (col1.startswith('Unnamed') or col1 == "School") else f"opp_{col2}" for col1, col2 in
                           temp_df.columns]
        # Adding home field.  1 if home, 0 if neutral, -1 if away
        temp_df.rename(columns={temp_df.columns[2]: 'Home'}, inplace=True)
        temp_df.Home = temp_df.Home.fillna(0).map({"@": -1, "N": 0, 0: 1}).astype(int)
        # Dropping unnecessary columns
        temp_df = temp_df.iloc[:, ~temp_df.columns.str.startswith('Unnamed')].drop('G', axis=1).dropna().query(
            "Date != 'Date'")
        temp_df['team_name'] = team_name.upper()
        # Rename columns
        temp_df.columns = MASTER_COLUMN_NAMES
        # Re-order columns
        temp_df = temp_df[MASTER_COLUMN_NAMES]
        # Coerce opponent name to uppercase
        temp_df.opp_name = temp_df.opp_name.map(str.upper)
        # Appending the cleaned dataframe back to the master data frame
        master_df = pd.concat([master_df, temp_df])

        # Increment counter
        counter += 1
        # Sleep and save if we've reached our random number
        if counter == stop_to_rest_point:
            sleep_time = np.random.randint(60, 120)
            logger.debug(f'Sleeping for {sleep_time} seconds')
            time.sleep(sleep_time)
            master_df.to_parquet(f'parquet_files/box_scores_sports_reference_{SEASON}.gzip', compression='gzip')
            continue

        # Sleep for 3 to 7 seconds
        time.sleep(np.random.randint(3, 7))

    master_df.to_parquet(f'parquet_files/box_scores_sports_reference_{SEASON}.gzip', compression='gzip')
    logger.info("Finished!")
    logger.info(f"{master_df.shape[0]} game box scores logged")


if __name__ == '__main__':
    main()
