from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from tqdm import tqdm
import time
from modules.log import create_logger
from modules.constants import MASTER_COLUMN_NAMES

SEASON = 2024

url_prefix = 'https://www.sports-reference.com'
logger = create_logger("StatusLogger", 'info')


def main() -> None:
    # Instantiate an empty dictionary
    team_name_id_dict = {}

    # URL for data from all schools
    all_schools_url = f'https://www.sports-reference.com/cbb/seasons/men/{SEASON}-school-stats.html'
    response = requests.get(all_schools_url, timeout=10)
    soup = BeautifulSoup(response.content)
    # Find table ('tr')
    table = soup.findAll('tr')

    logger.info("Getting unique team ID suffixes")
    # Iterate through rows
    for row in table:
        # Returns a None object if nothing is found
        search = row.find('a', href=True)
        # If we have something
        if search:
            # Extract the name and URL via string manipulation
            url_suffix = str(search).split('"')[1].replace(".html", "")
            team_name = str(search).split(">")[1].replace("</a", "").strip()
            # Update the dictionary
            team_name_id_dict[team_name] = url_suffix

    logger.info("Populating box scores from games played")
    # Instantiate empty data frame
    master_df = pd.DataFrame()
    # Create an iteration counter
    counter = 0
    # Create a random number between 100 and 300.  This is where the loop will pause
    # To not overload the site
    stop_to_rest_point = np.random.randint(20, 100)

    # Iterate through the dictionary
    for team_name, url_suffix in tqdm(team_name_id_dict.items()):

        full_url = f"{url_prefix}{url_suffix}-gamelogs.html"
        logger.debug(full_url)

        # If there are NO GAMES, move on
        try:
            temp_df = pd.read_html(full_url)[0]
        except ValueError as e:
            msg = str(e)
            if msg == "No tables found":
                logger.warning(f"Skipping {team_name} due to no data")
                continue
            raise

        # Surface-level data cleaning
        temp_df.columns = [col2 if (col1.startswith('Unnamed') or col1 == "School") else f"opp_{col2}" for col1, col2 in
                           temp_df.columns]
        temp_df = temp_df.iloc[:, ~temp_df.columns.str.startswith('Unnamed')].drop('G', axis=1).dropna().query(
            "Date != 'Date'")
        temp_df['team_name'] = team_name
        temp_df.columns = MASTER_COLUMN_NAMES
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


if __name__ == '__main__':
    main()
