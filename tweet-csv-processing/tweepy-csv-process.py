import pandas as pd
import time
import os
from datetime import date, datetime, timedelta

# TODO's:
# - Rename file, create docstrings, add comments, maybe rework method titles
# - Move helper functions into own file and create main.py
# - Implement basic sentiment analysis models and methods to run hourly/daily
# - experimaent normalising the data? (perhpas better done in a notebook)

# -------------------------------------------------------------------------------
# Methods
# -------------------------------------------------------------------------------


def get_hashtag_and_date_from_csv_title(csv_name):
    # region
    """Extracts hashtag (theme) and date from the csv file name or path.
    Assumes CSV names are formatted as done in the snscrape script:
    YYYY-MM-DD-hashtag-tweets.csv

    Args:
        csv_name (string): file name or file path

    Returns:
        hashtag (string): hashtag (theme) used in the csv title
        date (datetime.date): datetime date object
    """
    # endregion
    file_name = csv_name.split('/')[-1]
    hashtag = file_name.split('-')[-2]
    date = file_name.split(f'-{hashtag}')[0]
    date = datetime.fromisoformat(date).date()
    return hashtag, date


# -------------------------------------------------------------------------------

# TODO: I think a lot of the checks should be in this CSV import
def dataframe_from_tweet_csv(csv_path, sort_time_column=None):
    # region
    """Simply returns a pandas dataframe from csv file, optionally sort the
    dataframe by the time column provided.

    Args:
        csv_path (string): path to csv or csv name
        sort_time_column (string): CSV column title of time infor to sort

    Returns:
        pandas dataframe: a pandas dataframe
    """
    # endregion
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
        if len(error_df) > 0:
            print("there were some badly formatted tweets, these were removed")
            print(error_df)
            print(error_df.shape)
        df = no_error_df
        df = df.set_index(df[sort_time_column])
        df = df.sort_index()
    return df

# -------------------------------------------------------------------------------


def df_check_no_duplicates(dataframe):
    # region
    """Checks a dataframe for duplicates and raises exception on detection.

    Args:
        dataframe (pandas.DataFrame): A pandas DataFrame

    Raises:
        Exception: stops the program
    """
    # endregion
    if dataframe['id_str'].duplicated().any():
        raise Exception("This CSV has duplicate id's")
    return

# -------------------------------------------------------------------------------


def df_check_all_same_date(dataframe, file_date):
    # TODO: add time column parameter, rename 'file_date' make it general
    # region
    """Checks all dates in a dataframe are from the same date.

    Args:
        dataframe (pandas.DataFrame): A pandas DataFrame
        file_date ([type]): [description]

    Raises:
        Exception: [description]
    """
    # endregion
    df_dates = dataframe['created_at'].dt.date
    if df_dates.all() != file_date:
        raise Exception(
            f"Some tweets in the dataframe are not from {file_date}")
    return

# -------------------------------------------------------------------------------


def df_group_by_hour(dataframe, time_column):
    return dataframe.groupby(pd.Grouper(key=time_column, freq='H'))

# -------------------------------------------------------------------------------


def new_df_single_day_hourly_tweetcount(day_CSV_folder_path):
    # region
    """Returns a dataframe with the tweet count for each hashtag/file each hour
    for one day/folder of tweets (files and folders formatted as in
    snscrape/Tweepy method

    Args:
        day_CSV_folder_path ([type]): [description]
        day ([type], optional): [description]. Defaults to None.
    """
    # endregion
    file_names = os.listdir(day_CSV_folder_path)
    file_names.sort()
    # TODO: Could adapt this method to work for whole folder, or link to that function here
    count = 0
    output_df = pd.DataFrame()
    for file in file_names:
        coin, file_date = get_hashtag_and_date_from_csv_title(file)

        print(file)
        file_df = dataframe_from_tweet_csv(
            os.path.join(day_CSV_folder_path, file), 'created_at')
        print(f"Processing {len(file_df)} {coin} tweets from {file_date}")
        try:
            df_check_no_duplicates(file_df)
        except Exception:
            # TODO: handle this better or replace checking method with method to remove duplicates
            print("!!!!!!! Duplicates found!!!!!!!!!!!!!!!")
        try:
            df_check_all_same_date(file_df, file_date)
        except Exception:
            print("!!!!!!! Not all same date!!!!!!!!!!!!!!")
        file_df_hourly = df_group_by_hour(file_df, 'created_at')
        times = []
        counts = []
        for group, frame in file_df_hourly:
            times.append(group)
            counts.append(len(frame))

        if count == 0:
            hourly_count_dict = {'Time': times, f'{coin}': counts}
            output_df = pd.DataFrame(hourly_count_dict)
        else:
            output_df[f'{coin}'] = counts
        count += 1
    return output_df

# -------------------------------------------------------------------------------


def new_df_all_days_hourly_tweetcount(all_days_folder_path):
    output_df = pd.DataFrame()
    daily_tweet_folders = os.listdir(all_days_folder_path)
    daily_tweet_folders.sort(reverse=False)
    count = 0
    for folder in daily_tweet_folders:
        day_folder_path = os.path.join(all_days_folder_path, folder)
        single_day_df = new_df_single_day_hourly_tweetcount(day_folder_path)
        # print(single_day_df)
        if count == 0:
            output_df = single_day_df
        else:
            output_df = pd.concat(
                [output_df, single_day_df], ignore_index=True)
        count += 1
    return output_df


# -------------------------------------------------------------------------------
# Calls
# -------------------------------------------------------------------------------
current_folder = os.path.dirname(os.path.abspath(__file__))

tweepy_csv_master_folder = os.path.join(current_folder, "output-csv")

test_output_csv = os.path.join(current_folder, "test-out.csv")


df = new_df_all_days_hourly_tweetcount(tweepy_csv_master_folder)
print(df)
print(df.size)

df.to_csv(test_output_csv, index=False, header=True, mode='w+')


# -------------------------------------------------------------------------------
# testing
# -------------------------------------------------------------------------------# trouble_df = new_df_single_day_hourly_tweetcount(trouble_day_folder)

# trouble_day_folder = os.path.join(tweepy_csv_master_folder, '2021-02-16')

# print(tweepy_csv_master_folder)
# file_names = os.listdir(tweepy_csv_master_folder)
# print(file_names)
# print(os.path.split(current_folder)[0])
# print(os.path.dirname(current_folder))

# new_df_all_days_hourly_tweetcount()

# --------------------------------------------------
# df = new_df_single_day_hourly_tweetcount(os.path.join(current_folder, 'input-csv'))
# print(df)


# ------------------------------------------

# test_csv = os.path.join(current_folder, 'input-csv',
#                         '2021-02-11-ethereum-tweets.csv')
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
