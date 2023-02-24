import pandas as pd


def load_id_csv():

    # try:
    #     df = pd.read_csv('Adjustihg_Basketball_Stats/csvs/ids.csv')
    # except FileNotFoundError as e:
    #     try:
    #         pd.read_csv('/csvs/ids.csv')
    #     except FileNotFoundError as e:
    #         try:
    #             pd.read_csv('ids.csv')
    #         except FileNotFoundError as e:
    #             raise Exception("No dice on finding the right directory, sir")
    df = pd.read_csv('ids.csv')
    return df

if __name__ == "__main__":

    print(load_id_csv())