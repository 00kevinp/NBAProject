import re
from time import sleep
import numpy as np
import requests

from NBAProject import finding_data as fd
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


def main():

    game = "0022200620"
    box = fd.boxscoreadvancedv2.BoxScoreAdvancedV2(game_id=game)
    df = box.get_data_frames()
    team_adv = df[1]

    stats_to_keep = ["GAME_ID","TEAM_NAME","OFF_RATING", "DEF_RATING", "NET_RATING", "TS_PCT", "POSS", "PIE"]

    team_subset = team_adv[stats_to_keep]
    # print(team_subset)

    og_df = pd.read_csv("stats/cleaned_regseason_no_covid.csv")

    game_ids = set()

    for gg in og_df["GAME_ID"]:
        game_ids.add(str(gg))


    game_ids = sorted(game_ids)

    adv_stats = []

    count = last_game = 0
    for gid in game_ids:
        while count < 600:
            gid = "00" + gid
            last_game = int(gid)
            try:
                box = fd.boxscoreadvancedv2.BoxScoreAdvancedV2(game_id=gid)
                df = box.get_data_frames()
                team_adv = df[1]
                adv_stats.append(team_adv[stats_to_keep])
                print(f"Fetching {gid} ...")
                sleep(3)
                count += 1
                break
            except requests.exceptions.ReadTimeout:
                # back up in case sudden failure -- still write progress to file
                adv_stats_df = pd.concat(adv_stats)
                adv_stats_df.to_csv("adv_stats_progress.csv", mode='a',index=False)
                print(f"Critical error. Last game: {last_game}")
                break

    print(f"Last game: {last_game}")
    with open("file.txt", "a") as f:
        f.write(str(last_game))
    adv_stats_df = pd.concat(adv_stats)
    adv_stats_df.to_csv("adv_stats_progress.csv", mode='a', index=False)


if __name__ == '__main__':
    main()