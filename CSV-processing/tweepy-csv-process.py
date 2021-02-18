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


def dataframe_from_tweet_csv(csv_path, sort_time_column=None):
    """Simply returns a pandas dataframe from csv file, optionally sort the
    dataframe by the time column provided.

    Args:
        csv_path (string): path to csv or csv name
        sort_time_column (string): CSV column title of time infor to sort

    Returns:
        pandas dataframe: a pandas dataframe
    """
    # , dtype='string', chunksize=4000, low_memory=False)
    # df = pd.read_csv(csv_path)

    df = pd.DataFrame()

    # chunked CSV passong to dataframe, as had some vague errors when not done
    for chunk in pd.read_csv(csv_path, chunksize=4000):
        df = df.append(chunk)

    if sort_time_column:
        # 'coerce' used as had a column error - string 'en' in the date field
        # likely ueser_lang somehow ended up in the date colum...
        # TODO: investigate this further and maybe separate out dropped columns for inspection
        df[sort_time_column] = pd.to_datetime(
            df[sort_time_column], errors='coerce')
        # dropping anomolous rows
        # https://stackoverflow.com/questions/34296292/pandas-dropna-store-dropped-rows
        no_error_df = df.dropna(subset=[sort_time_column])
        error_df = df[~df.index.isin(no_error_df.index)]
        print(error_df)
        df = no_error_df
        df = df.set_index(df[sort_time_column])
        df = df.sort_index()
    return df


def df_check_no_duplicates(dataframe):
    # detect any duplicate id's:
    if dataframe['id_str'].duplicated().any():
        raise Exception("This CSV has duplicate id's")
    return


def df_check_all_same_date(dataframe, file_date):
    df_dates = dataframe['created_at'].dt.date
    if df_dates.all() != file_date:
        raise Exception(
            f"Some tweets in the dataframe are not from {file_date}")
    return


def df_group_by_hour(dataframe, time_column):
    return dataframe.groupby(pd.Grouper(key=time_column, freq='H'))


def new_df_hourly_tweetcount_day(CSV_folder_path, day=None):
    file_names = os.listdir(CSV_folder_path)
    # TODO: Could adapt this method to work for whole folder, or link to that function here
    count = 0
    output_df = pd.DataFrame()
    for file in file_names:
        coin, file_date = get_hashtag_and_date_from_csv_title(file)
        print(file)
        file_df = dataframe_from_tweet_csv(
            os.path.join(CSV_folder_path, file), 'created_at')
        print(f"Processing {len(file_df)} {coin} tweets from {file_date}")
        df_check_no_duplicates(file_df)
        df_check_all_same_date(file_df, file_date)
        count += 1
    return


# -------------------------------------------------------------------------------
# Calls
# -------------------------------------------------------------------------------
current_folder = os.path.dirname(os.path.abspath(__file__))
test_csv = os.path.join(current_folder, 'input-csv',
                        '2021-02-11-ethereum-tweets.csv')

# coin, file_date = get_hashtag_and_date_from_csv_title(test_csv)

# print(f"Processing {coin} tweets from {file_date}")
# df = dataframe_from_tweet_csv(test_csv, 'created_at')
# df_check_no_duplicates(df)
# df_check_all_same_date(df, file_date)
# df_hourly = df_group_by_hour(df, 'created_at')

# times = []
# counts = []

# for group, frame in df_hourly:
#     # print(group.time())
#     times.append(group)
#     counts.append(len(frame))

# flumposhire = {'times': times, f'{coin}': counts}

# dflump = pd.DataFrame(flumposhire)


new_df_hourly_tweetcount_day(os.path.join(current_folder, 'input-csv'))


# print(dflump)
# print(len(df))
# file_names = os.listdir(os.path.join(current_folder, 'input-csv'))
# print(file_names)

# file_names = os.listdir("../Tweepy/csv-tweet-files")
# print(file_names)

# print(dflump)
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
