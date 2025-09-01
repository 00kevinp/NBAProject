from NBAProject import finding_data as fd


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
    seasons = ["2012-13","2013-14", "2014-15", "2015-16", "2016-17", "2017-18", "2018-19", "2021-22","2022-23", "2023-24", "2024-25"]
    df = fd.get_game_ids_for_seasons(seasons)
    fd.panda_df_to_csv(df)



if __name__ == '__main__':
    main()