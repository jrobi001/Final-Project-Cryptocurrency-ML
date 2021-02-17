import pandas as pd
import time
import os
from datetime import date, datetime, timedelta

# -------------------------------------------------------------------------------
# Methods
# -------------------------------------------------------------------------------


def get_hashtag_and_date_from_csv_title(csv_name):
    """Extracts hashtag (theme) and date from the csv file name or path. 
    Assumes CSV names are formatted as done in the snscrape script: 
    YYYY-MM-DD-hashtag-tweets.csv

    Args:
        csv_name (string): file name or file path

    Returns:
        hashtag (string): hashtag (theme) used in the csv title
        date (datetime.date): datetime date object
    """
    file_name = csv_name.split('/')[-1]
    hashtag = file_name.split('-')[-2]
    date = file_name.split(f'-{hashtag}')[0]
    date = datetime.fromisoformat(date).date()
    return hashtag, date


# -------------------------------------------------------------------------------


def dataframe_from_tweet_csv(csv_path, sort_column=None):
    """Simply returns a pandas dataframe from csv file, optionally sort by the column 
    title provided.

    Args:
        csv_path ([type]): [description]
        sort_column ([type]): [description]

    Returns:
        pandas dataframe: [description]
    """
    # , dtype='string', chunksize=4000, low_memory=False)
    df = pd.read_csv(csv_path)

    # sort by time/ sort columnn
    if sort_column:
        df[sort_column] = pd.to_datetime(df[sort_column])
        df = df.set_index(df[sort_column])
        df = df.sort_index()
    return df


def df_check_no_duplicates(dataframe):
    # detect any duplicate id's:
    if dataframe['id_str'].duplicated().any():
        raise Exception("This CSV has duplicate id's")
    else:
        print("No duplicate tweet ids")
    return


def df_check_all_same_date(dataframe, file_date):
    df_dates = dataframe['created_at'].dt.date
    if df_dates.all() != file_date:
        raise Exception(
            f"Some tweets in the dataframe are not from {file_date}")
    else:
        print(f"All tweets from {file_date}")
    return


def df_group_by_hour(dataframe, time_column):
    return dataframe.groupby(pd.Grouper(key=time_column, freq='H'))


# -------------------------------------------------------------------------------
# Calls
# -------------------------------------------------------------------------------
current_folder = os.path.dirname(os.path.abspath(__file__))
test_csv = os.path.join(current_folder, 'input-csv',
                        '2021-02-11-ethereum-tweets.csv')

coin, file_date = get_hashtag_and_date_from_csv_title(test_csv)

print(f"Processing {coin} tweets from {file_date}")
df = dataframe_from_tweet_csv(test_csv, sort_column='created_at')
df_check_no_duplicates(df)
df_check_all_same_date(df, file_date)
df_hourly = df_group_by_hour(df, 'created_at')

for group, frame in df_hourly:
    print(group)
    print(len(frame))

# print(dates == file_date)
# date = date.date()
# print(dates)
# boolean = df['id_str'].duplicated().any()
# print(boolean)

# -------------------------------------------------------------------------------
# testing
# -------------------------------------------------------------------------------

# test1 = os.path.join(current_folder, 'input-csv',
#                      '2021-02-11-ethereum-tweets.csv')
# test2 = './input-csv/2021-02-11-ethereum-tweets.csv'
# test3 = '2021-02-11-ethereum-tweets.csv'

# coin1, date1 = print(get_hashtag_and_date_from_csv_title(test1))
# coin2, date2 = get_hashtag_and_date_from_csv_title(test2)
# coin3, date3 = get_hashtag_and_date_from_csv_title(test3)

# print(coin1, date1)
# print(coin2, date2)
# print(coin3, date3)
