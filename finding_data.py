# GOAL FOR TODAY:
# Display a window with a search bar


# Project Overview
# A search window will appear with a prompt, asking for a current or former NBA players name
# Once the name is entered and the user hits search, the window should transform into a page,
# listing the players former and current statistics, along with the team(s) and year of the season ex: 23-24 (2023-2024)

# I will request info from websites to extract the correct data, and list it accordingly.

# Show progress from a players year-to-year stats by using graphs to display data
import os
import tkinter as tk
from time import sleep, time
from tkinter import ttk
import numpy as np
import pandas as pd
import nba_api
import requests
from nba_api.stats.endpoints import *
from nba_api.stats.static import players
from nba_api.stats.static import teams as tm

nbaPlayers = players.get_players()
nbaTeams = tm.get_teams()

global last_game

def df_to_csv(df, file_name):
    df.to_csv(file_name, index=False)


def search_player(playerName):
    # print(f"searching for {playerName}")
    player = [player for player in nbaPlayers if player["full_name"] == playerName][0]
    print(player)

def find_team(team_name):
    return tm._find_team_by_abbreviation(team_name)

def find_playerID(playerName):
    player = [player for player in nbaPlayers if player["full_name"] == playerName][0]
    playerID = (player["id"])
    return playerID


def efg(playerID):
    career = playercareerstats.PlayerCareerStats(player_id=playerID)
    stats = career.get_data_frames()[0]
    efg = (stats["FGM"] + 0.5 * (stats["FG3M"])) / stats["FGA"]
    return efg

def find_player_stats(playerID):
    career = playercareerstats.PlayerCareerStats(player_id=playerID)
    stats = career.get_data_frames()[0] # add a second [] with the stat you want
    pd.set_option("display.max.columns", None)
    pd.set_option("display.max.rows", None)
    print(stats.to_string())


def get_game_ids(seasons, season_type="Regular Season"):
    """
    Returns all unique GAME_IDs for a given NBA season.
    season format: 'YYYY-YY' (e.g., '2023-24')
    season_type: 'Regular Season', 'Playoffs', 'Pre Season', 'All Star'
    """
    log = leaguegamelog.LeagueGameLog(
        season=seasons,
        season_type_all_star=season_type
    )
    df = log.get_data_frames()[0]
    game_ids = sorted(df['GAME_ID'].unique().tolist())

    return game_ids



def get_game_ids_for_seasons(seasons):
    # seasons in format 2000-01, season_type = "Regular Season" by default through get_game_ids method
    all_game_ids = {}

    for season in seasons:
        ids = get_game_ids(season)
        all_game_ids[season] = ids
        print(f"{season} contained {len(ids)} games")

    df = pd.DataFrame(all_game_ids)
    return df


pd.set_option('display.max_columns', None)  # show all columns
pd.set_option('display.max_rows', None)     # show all rows
pd.set_option('display.width', None)        # don't wrap lines
pd.set_option('display.max_colwidth', None)
def game_details_boxscore(game_id):

    bs = boxscoresummaryv2.BoxScoreSummaryV2(game_id=game_id)
    print(f"Game Summary: {bs.game_summary.get_data_frame()} ")
    print(f"Line Score Summary: {bs.line_score.get_data_frame()}")



def melt_game_id_csv(game_id_csv):

    df = pd.read_csv(game_id_csv)
    df_game_ids = df.melt(var_name="Seasons", value_name="GAME_ID")

    df_game_ids = df_game_ids.dropna()
    game_ids_list = df_game_ids["GAME_ID"].astype(str).tolist()

    return game_ids_list


def game_details_team_stats(game_ids, progress_file="progressv3.csv"):

    file_exists = os.path.isfile(progress_file)
    for game_id in game_ids:
        print(f"Getting info for game ID {game_id}")
        team_stats = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
        df = team_stats.team_stats.get_data_frame()
        df['GAME_ID'] = game_id

        df.to_csv(progress_file, mode="a", header=not file_exists, index=False)
        file_exists = True
        sleep(1.0)

def delete_me(game_id):
    team_stats = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
    df = team_stats.team_stats.get_data_frame()
    return df

def iterate_over_csv(csv_file, retries=4):
    all_game_team_stats = []
    counter = 0
    # df = pd.read_csv(csv_file, dtype=str)
    for i in range(1, 3):
        df = pd.read_csv(csv_file, dtype={f"C{i}":str})
        for game_id in df[f"C{i}"]:
            print(f"Fetching data for game ID: {game_id}")
            attempts = 0
            while attempts < retries:
                try:
                    team_stats = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
                    df = team_stats.team_stats.get_data_frame()
                    # values can be added like below using df[new column name] = what we want to manipulate
                    # df["fg%"] = df["FGM"] / df["FGA"]
                    all_game_team_stats.append(df)
                    sleep(.6)
                    counter += 1
                    # print(f"Count: {counter}")
                    if counter >= 580:
                        sleep(600)
                        counter = 0
                    break # successful --> break out
                except requests.exceptions.ReadTimeout:
                    attempts += 1
                    print(f"timeout on game {game_id}, retry {retries-attempts}")
                    sleep(3)
            else:
                print(f"Skipping game {game_id} after {retries} retries")

    return pd.concat(all_game_team_stats, ignore_index=True)




def flattendf():
    df = pd.read_csv("stats/reg_season_game_ids_13-25.csv", dtype=str)
    all_game_ids = []
    for col in df.columns:
        ids = df[col].dropna().tolist()
        all_game_ids.extend(ids)

    return all_game_ids
def iterate_over_csv_in_batchesv2(batch_size, all_game_ids, last_game):


    all_game_stats = []

    all_game_ids = all_game_ids[last_game:]

    print(f"starting at index: {last_game}")
    print(f"translates to game ID: {all_game_ids[0]}")

    for i in range(0, len(all_game_ids), batch_size):
        batch = all_game_ids[i:i + batch_size]
        for game_id in batch:
            print(f"Fetching data for game ID: {game_id}")
            success = True

            while success:
                try:
                    team_stats = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
                    stats_df = team_stats.team_stats.get_data_frame()
                    all_game_stats.append(stats_df)
                    last_game = game_id
                    sleep(0.6)
                except requests.exceptions.ReadTimeout:
                    success = False
                    print(f"Timeout on game {game_id}, retrying...")
                    sleep(3)

            if not success:
                print(f"Skipping game {game_id} after 3 failed attempts.")

        # save progress after each batch
        pd.concat(all_game_stats, ignore_index=True).to_csv("progress.csv", index=False)
        with open("last_game.txt", "w") as f:
            f.write(last_game)

    return pd.concat(all_game_stats, ignore_index=True)



def tracking_advanced_metrics():
    game = "0022200620"
    box = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id=game)
    df = box.get_data_frames()
    team_adv = df[1]

    stats_to_keep = ["GAME_ID", "TEAM_NAME", "OFF_RATING", "DEF_RATING", "NET_RATING", "TS_PCT", "POSS", "PIE"]

    team_subset = team_adv[stats_to_keep]
    # print(team_subset)

    og_df = pd.read_csv("stats/cleaned_regseason_no_covid.csv")

    game_ids = set()

    for gg in og_df["GAME_ID"]:
        game_ids.add(str(gg))

    game_ids = sorted(game_ids)

    adv_stats = []

    count = last_game = 0
    for gid in game_ids[1200:]:
        while count < 600:
            gid = "00" + gid
            last_game = int(gid)
            try:
                box = boxscoreadvancedv2.BoxScoreAdvancedV2(game_id=gid)
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
                adv_stats_df.to_csv("adv_stats_progress.csv", mode='a', index=False)
                print(f"Critical error. Last game: {last_game}")
                break

    print(f"Last game: {last_game}")
    with open("file.txt", "a") as f:
        f.write(str(last_game))
    adv_stats_df = pd.concat(adv_stats)
    adv_stats_df.to_csv("adv_stats_progress.csv", mode='a', index=False)

def create_data_points_win_pct():
    # use this to gather game_ids we want, and create a running stat win_pct in a new column

    df = pd.read_csv("/Users/kevinpickelman/PycharmProjects/NBAStatsProject/stats/cleaned_regularseason_stats.csv")
    games = []
    # games have the format of 21200001
    # 2{season}{game}
    # if len game is less than 4, pad 1 zero (21200999)
    # else less than 3, pad 2 zeros (21200099)
    # less than 2 pad 3 zeros (21200009)
    game_prefix_2012 = "2120"
    for i in range(1,1231):
        game = game_prefix_2012 + str(i).zfill(5)
        games.append(game)

    for gg in games:
        print(df[gg])



def get_covid_games():
    df = pd.read_csv("stats/covid_seasons_game_ids.csv")

    game_ids = set()

    for gg in df["GAME_ID"]:
        game_ids.add(str(gg))

    game_ids = sorted(game_ids)

    stats = []

    count = last_game = 0
    for gid in game_ids[1800:2139]:

        while count < 600:
            last_game = int(gid)
            print(f"Fetching {last_game}")
            try:
                box = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=gid)
                df = box.get_data_frames()[1]
                stats.append(df)
                # print(stats)
                sleep(2)
                count += 1
                break
            except requests.exceptions.ReadTimeout:
                # back up in case sudden failure -- still write progress to file
                stats_df = pd.concat(stats)
                stats_df.to_csv("covid_stats_progress.csv", index=False, mode='a')
                print(f"Critical error. Last game: {last_game}")
                break

    print(f"Last game: {last_game}")
    with open("last_game.txt", "a") as f:
        f.write(str(last_game))
    pd.concat(stats).to_csv("covid_stats_progress.csv", index=False, mode='a')


def PIE_formula():

    # PIE formula = (PTS + FGM + FTM – FGA – FTA + Deff.REB + Off.REB/2 + AST + STL + BLK/2 – PF – TO)
    #       / (Game.PTS + Game.FGM + Game.FTM – Game.FGA – Game.FTA + Game.Deff.REB + Game.Off.REB/2
    #       + Game.AST + Game.STL + Game.BLK/2 – Game.PF – Game.TO)

    df = pd.read_csv("NBAProject/stats/covid_data.csv")
    game_totals = df.groupby("GAME_ID").sum(numeric_only=True).reset_index()
    df = df.merge(game_totals, on="GAME_ID", suffixes=("", "_game"))
    df["PIE"] = (
            (df["PTS"] + df["FGM"] + df["FTM"] - df["FGA"] - df["FTA"] +
             df["DREB"] + (df["OREB"] / 2) + df["AST"] + df["STL"] +
             (df["BLK"] / 2) - df["PF"] - df["TO"]) /
            (df["PTS_game"] + df["FGM_game"] + df["FTM_game"] - df["FGA_game"] - df["FTA_game"] +
             df["DREB_game"] + (df["OREB_game"] / 2) + df["AST_game"] + df["STL_game"] +
             (df["BLK_game"] / 2) - df["PF_game"] - df["TO_game"])
    )  * 100

    df["PIE"] = df["PIE"].round(2)

    df.drop(columns=[col for col in df.columns if col.endswith("_game")], inplace=True)
    # drop old labels from game totals

    df.to_csv("NBAProject/stats/cleaned_covidseasons_with_PIE.csv", index=False)



def indicate_covid():
    df_ = pd.read_csv("NBAProject/stats/final_covid_data.csv")
    df = pd.read_csv("NBAProject/stats/final_regseason_data.csv")

    df_["COVID_FLAG"] = 1
    df['COVID_FLAG'] = 0

    combined_df = pd.concat([df, df_], ignore_index=True)
    combined_df = combined_df.sort_values(by="GAME_ID").reset_index(drop=True)


    combined_df.to_csv("NBAProject/stats/combined_final_data.csv", index=False)


def make_home_team_col():
    df = pd.read_csv("NBAProject/stats/Games.csv")
    my_df = pd.read_csv("NBAProject/stats/combined_final_data.csv")

    df['gameId'].rename('GAME_ID')
    merged = my_df.merge(
        df[['gameId', 'hometeamName']],
        left_on='GAME_ID',
        right_on='gameId',
        how='left'
    )

    merged = merged.drop(columns=['gameId'])
    merged.to_csv("NBAProject/stats/combined_final_dataV2.csv")



def rename_home_team_col():
    df = pd.read_csv("NBAProject/stats/combined_final_dataV2.csv")
    df.rename(columns={'hometeamName': 'HOME_TEAM'}, inplace=True)
    df.to_csv("NBAProject/stats/combined_final_dataV2.csv")

def move_around_columns():
    df = pd.read_csv("NBAProject/stats/combined_final_dataV2.csv")
    col_to_move = df.pop('HOME_TEAM')  # Remove 'ColC' and store its data
    df.insert(5, 'HOME_TEAM', col_to_move)  # Insert 'ColC' at index 1
    df.to_csv("NBAProject/stats/combined_final_dataV2.csv")

if __name__ == '__main__':
    move_around_columns()