import re
from time import sleep

from NBAProject import finding_data as fd
import os
import pandas as pd

def main():
    # root = tk.Tk()
    # root.title("NBA Statistics Search")
    # mainWindow = ttk.Frame(root, padding='10 10 10 10')
    # mainWindow.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    #
    # searchLabel = ttk.Label(mainWindow, text="Enter a current or former NBA player's name...")
    # searchLabel.grid(column=1, row=1, sticky=tk.W)



    df = pd.read_csv("2012-24reg_season_statsv2.csv")

    x1 = set()
    missing_vals = set()
    for g_id in fd.flattendf():
        x1.add(int((re.sub('^0+','',g_id))))

    x2 = set()
    for gg_id in df['GAME_ID']:
        x2.add(gg_id)

    # print(f"x1: {x1}")
    # print(f"x2: {x2}")


    missing_vals = (x1-x2)








if __name__ == '__main__':
    main()