import json
import pandas as pd
import requests
from modules.log import create_logger
import numpy as np
import time
from tqdm import tqdm
from modules.objects import TeamPlayerDataframeHub

# Pull in the team:UI JSON file
with open('json_files/team_uis.json', 'r') as f:
    team_name_id_dict = json.load(f)
# Create a logger
logger = create_logger("StatusLogger", 'info')


def main() -> None:
    output_dict = {}
    stop_to_rest_counter = 0
    for team_name, ui in tqdm(team_name_id_dict.items()):

        url = f'https://www.sports-reference.com/cbb/schools/{ui}/men/2024.html#all_roster'
        logger.debug(team_name,url)
        r = requests.get(url)

        try:
            dfs = pd.read_html(r.text)
        # If there are no tables, a ValueError is returned
        except ValueError as e:
            logger.debug(f"Skipping {team_name} as no tables were found")
            time.sleep(np.random.randint(4, 6))
            continue

        hub = TeamPlayerDataframeHub(team_name='Purdue',
                                     player_info=dfs[0],
                                     player_per_game_simple=dfs[3],
                                     player_totals=dfs[4],
                                     player_per_100_possessions=dfs[6],
                                     player_advanced=dfs[7])
        output_dict[team_name.upper()] = hub.to_dict()
        time.sleep(np.random.randint(4, 6))

        stop_to_rest_counter += 1
        if stop_to_rest_counter == 30:
            time_to_sleep = np.random.randint(20, 40)
            logger.debug(f"Sleeping for {time_to_sleep} seconds")
            time.sleep(time_to_sleep)
            stop_to_rest_counter = 0


if __name__ == '__main__':
    main()
