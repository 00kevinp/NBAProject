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
    print(len(df))
    print(len(fd.flattendf()) * 2)
    print((len(fd.flattendf()) * 2) - len(df))
    # 72 games missing from our data frame


    # for n in fd.flattendf():
    #     if n not in df and n :
    #         print(n)

#     size difference, need to figure out why






if __name__ == '__main__':
    main()