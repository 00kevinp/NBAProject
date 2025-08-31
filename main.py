import finding_data as fd


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
    df = fd.get_game_ids("2023-2024", season_type="Playoffs")
    print(df)



if __name__ == '__main__':
    main()