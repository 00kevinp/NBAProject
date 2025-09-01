# GOAL FOR TODAY:
# Display a window with a search bar


# Project Overview
# A search window will appear with a prompt, asking for a current or former NBA players name
# Once the name is entered and the user hits search, the window should transform into a page,
# listing the players former and current statistics, along with the team(s) and year of the season ex: 23-24 (2023-2024)

# I will request info from websites to extract the correct data, and list it accordingly.

# Show progress from a players year-to-year stats by using graphs to display data

import tkinter as tk
from time import sleep
from tkinter import ttk
import pandas as pd
import nba_api
from nba_api.stats.endpoints import playercareerstats, boxscoresummaryv2, leaguegamelog
from nba_api.stats.static import players
from nba_api.stats.static import teams as tm

nbaPlayers = players.get_players()
nbaTeams = tm.get_teams()
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

def get_game_ids_for_seasons(seasons):

    for season in seasons:
        ids = get_game_ids(season)
        all_game_ids[season] = ids
        print(f"{season} contained {len(ids)} games")


    df = pd.DataFrame(all_game_ids)
    return df

def panda_df_to_csv(df):
    df.to_csv('regular_season_game_ids_2013-2025.csv', index=False)







