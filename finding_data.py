# GOAL FOR TODAY:
# Display a window with a search bar


# Project Overview
# A search window will appear with a prompt, asking for a current or former NBA players name
# Once the name is entered and the user hits search, the window should transform into a page,
# listing the players former and current statistics, along with the team(s) and year of the season ex: 23-24 (2023-2024)

# I will request info from websites to extract the correct data, and list it accordingly.

# Show progress from a players year-to-year stats by using graphs to display data

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


all_game_ids = {}
all_game_stats = {}

def get_game_ids_for_seasons(seasons):

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
    print(f"Other Stats Summary: {bs.other_stats.get_data_frame()}")
    print(f"Team Stats Summary: {bs.team_stats.get_data_frame()}")



def melt_game_id_csv(game_id_csv):

    df = pd.read_csv(game_id_csv)
    df_game_ids = df.melt(var_name="Seasons", value_name="GAME_ID")

    df_game_ids = df_game_ids.dropna()
    game_ids_list = df_game_ids["GAME_ID"].astype(str).tolist()

    return game_ids_list


def game_details_team_stats(game_ids):

    all_game_team_details = []
    for game_id in game_ids:
        team_stats = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
        df = team_stats.team_stats.get_data_frame()
        df['GAME_ID'] = game_id
        all_game_team_details.append(df)


    return pd.concat(all_game_team_details, ignore_index=True)


def iterate_over_csv(csv_file, retries=4):
    all_game_team_stats = []
    counter = 0
    # df = pd.read_csv(csv_file, dtype=str)
    for i in range(1, 12):
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



