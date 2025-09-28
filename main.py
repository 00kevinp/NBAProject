import re
from time import sleep

import numpy as np
from nba_api.stats.endpoints import boxscoretraditionalv2

from NBAProject import finding_data as fd
import os
import pandas as pd

def main():


    all_stats = pd.read_csv("2012-24reg_season_statsv2.csv")


    missing_stats = pd.read_csv("missing_game_stats.csv")
    # print(missing_stats)


    combined_df = pd.concat([all_stats, missing_stats])
    combined_df = combined_df.sort_values(by=['GAME_ID']).reset_index(drop=True)

    final_file = combined_df.to_csv("final_stats_no_covid.csv")

if __name__ == '__main__':
    main()