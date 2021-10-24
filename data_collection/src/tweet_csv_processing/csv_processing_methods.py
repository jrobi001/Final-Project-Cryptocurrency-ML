import pandas as pd
import os
from datetime import datetime
import csv

# TODO's:
# - Create docstrings, add comments, maybe rework method titles
# - experimaent normalising the data? (perhpas better done in a notebook)


# ------------------------------------------------------------------------------
# Delete Bad Tweet Methods
# ------------------------------------------------------------------------------


def print_indexes_of_bad_format_tweets(csv_path):
    file_name = csv_path.split('/')[-1]
    print(file_name)
    with open(csv_path) as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        line = 0
        count = 0
        good_len = 0
        for row in reader:
            line += 1
            # print(line)
            # print(row)
            if line == 1:
                good_len = len(row)
                print(good_len)
            if row == []:
                continue
            if len(row) != good_len:
                print(f"bad tweet on line {line}")
                count += 1
        print(f"total bad tweets = {count}")
    return

# ------------------------------------------------------------------------------


def print_bad_tweets_all_csvs(master_folder_path):
    daily_tweet_folders = os.listdir(master_folder_path)
    daily_tweet_folders.sort(reverse=True)
    for folder in daily_tweet_folders:
        day_folder_path = os.path.join(master_folder_path, folder)
        file_names = os.listdir(day_folder_path)
        file_names.sort()
        for file in file_names:
            file_path = os.path.join(day_folder_path, file)
            print_indexes_of_bad_format_tweets(file_path)
            print("-"*80)
    return

# ------------------------------------------------------------------------------


def delete_bad_tweets_csv(input_csv_path, output_csv_path):
    file_name = input_csv_path.split('/')[-1]
    print(file_name)
    with open(input_csv_path) as csv_file, open(output_csv_path, 'w') as out:
        writer = csv.writer(out)
        reader = csv.reader(csv_file, delimiter=',')
        line = 0
        count = 0
        good_len = 0
        for row in reader:
            line += 1
            if line == 1:
                good_len = len(row)
            if row == []:
                continue

            if len(row) != good_len:
                print(f"bad tweet on line {line} removed")
                count += 1
            else:
                writer.writerow(row)
        print(f"total bad tweets = {count}")
    return

# ------------------------------------------------------------------------------


def delete_bad_tweets_all_csvs_create_new(input_master_folder, output_master_folder, only_process_new=False):
    input_tweet_folders = os.listdir(input_master_folder)
    input_tweet_folders.sort(reverse=True)

    for folder in input_tweet_folders:
        input_day_folder_path = os.path.join(input_master_folder, folder)
        file_names = os.listdir(input_day_folder_path)
        file_names.sort()

        output_day_folder_path = os.path.join(output_master_folder, folder)
        if not os.path.exists(output_day_folder_path):
            os.makedirs(output_day_folder_path)

        for file in file_names:
            input_file_path = os.path.join(input_day_folder_path, file)
            output_file_path = os.path.join(output_day_folder_path, file)

            # if file already exists, don't process
            if only_process_new == True:
                if os.path.exists(output_file_path):
                    continue

            delete_bad_tweets_csv(input_file_path, output_file_path)
    return


# ------------------------------------------------------------------------------
# Processing Methods
# ------------------------------------------------------------------------------


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


# ------------------------------------------------------------------------------

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
        df = df_sort_datetime_column(df, sort_time_column)
    return df

# ------------------------------------------------------------------------------


def df_sort_datetime_column(df, datetime_column):
    # 'coerce' used as badly formatted tweets were created with data in wrong
    # columns occasionally (by users using strange charecters in tweets)
    # (most of these have now been filtered out at collection time)
    df[datetime_column] = pd.to_datetime(df[datetime_column], errors='coerce')
    # dropping anomolous rows
    # https://stackoverflow.com/questions/34296292/pandas-dropna-store-dropped-rows
    no_error_df = df.dropna(subset=[datetime_column])
    error_df = df[~df.index.isin(no_error_df.index)]
    if len(error_df) > 0:
        print("there were some tweets with bad timestamps, these were removed")
        print(error_df)
        print(error_df.shape)
    df = no_error_df
    df = df.set_index(df[datetime_column])
    df = df.sort_index()
    return df


# ------------------------------------------------------------------------------


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

# ------------------------------------------------------------------------------


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

# ------------------------------------------------------------------------------


def df_group_by_hour(dataframe, time_column):
    return dataframe.groupby(pd.Grouper(key=time_column, freq='H'))

# ------------------------------------------------------------------------------


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
            hourly_count_dict = {'datetime': times, f'{coin}': counts}
            output_df = pd.DataFrame(hourly_count_dict)
        else:
            output_df[f'{coin}'] = counts
        count += 1
    return output_df

# ------------------------------------------------------------------------------


def new_df_all_days_hourly_tweetcount(all_days_folder_path):
    """returns a dataframe with a count of the tweets per hour for each coin. 
    file names should be in the format of the twitter scraper: YYYY-MM-DD-COINNAME-tweets.csv.
    Assumes files are stored in date folders. columns are set to the 'COINNAME' in the csv title.

    Args:
        all_days_folder_path (string): absolute or relative path to the master tweet folder to process

    Returns:
        pandas.DataFrame: dataframe of tweetcounts per hour for each coin identifed from the files passed
    """
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


# ------------------------------------------------------------------------------


def get_last_date_csv(csv_file_path, time_column):
    file_df = dataframe_from_tweet_csv(csv_file_path, time_column)
    # could be rewritten as a single step, but
    date = file_df[time_column].dt.date.max()
    return date


# ------------------------------------------------------------------------------
# testing
# ------------------------------------------------------------------------------
# # trouble_df = new_df_single_day_hourly_tweetcount(trouble_day_folder)

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
