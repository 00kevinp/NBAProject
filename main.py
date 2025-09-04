from NBAProject import finding_data as fd

import pandas as pd

def main():
    # root = tk.Tk()
    # root.title("NBA Statistics Search")
    # mainWindow = ttk.Frame(root, padding='10 10 10 10')
    # mainWindow.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    #
    # searchLabel = ttk.Label(mainWindow, text="Enter a current or former NBA player's name...")
    # searchLabel.grid(column=1, row=1, sticky=tk.W)

    # playerName = input("Which player do you want to search for?\n")
    # searchPlayer(playerName)
    # fd.find_player_stats(2544)
    # print(fd.efg(2544))
    # seasons = ["2024-25"]
    # df = fd.get_game_info(seasons)
    # print(df.head())

    df = fd.iterate_over_csv("reg_season_game_ids_13-25.csv")
    fd.df_to_csv(df, "team_stats_reg_season_no_covid.csv")
    print("Data saved to team_stats_reg_season_no_covid.csv")
    print(df)




if __name__ == '__main__':
    main()