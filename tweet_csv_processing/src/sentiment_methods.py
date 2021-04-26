from datetime import time
from .csv_processing_methods import *
import pandas as pd
import os
import re
import numpy as np
from textblob import TextBlob

# TODO:
# - Adapt sentiment method to create hourly and daily breakdowns at the same time
# - Adapt sentiment method to only run on 'new' tweets - append to the old file
# - maybe try running a different sentiment model
# - Add docstrings, comments etc.


def clean_text(text, remove_mentions=True, remove_hashtags=True, remove_links=True, filter_alphanumeric=True):
    cleaned = ""
    for word in text.split():
        if len(word) < 1:
            continue
        elif word[0] == '@' and remove_mentions:
            continue
        elif word[0] == '#' and remove_hashtags:
            continue
        elif word[0:8] == "https://" and remove_links:
            continue
        else:
            cleaned = cleaned + ' ' + word
    if filter_alphanumeric:
        cleaned = re.sub(r'\W+', ' ', cleaned)
    return cleaned


# ------------------------------------------------------------------------------


def sentiment_df_from_tweet_df(tweet_dataframe, clean_tweets=True):
    # only english tweets:
    tweet_dataframe = tweet_dataframe.loc[tweet_dataframe["user_lang"] == "en"]
    # drop all columns other than text:
    tweet_dataframe = tweet_dataframe["text"]
    # dropping any duplicates
    tweet_dataframe = tweet_dataframe.drop_duplicates()
    # cleaning tweets (if chosen)
    if clean_tweets == True:
        tweet_dataframe = tweet_dataframe.apply(clean_text)

    tweet_dataframe['sentiment'] = tweet_dataframe.apply(
        lambda text: TextBlob(text).sentiment)

    sentiment_list = tweet_dataframe['sentiment'].tolist()
    sentiment_columns = ['polarity', 'subjectivity']

    sentiment_only_df = pd.DataFrame(sentiment_list, columns=sentiment_columns)
    return sentiment_only_df


# ------------------------------------------------------------------------------


def mean_polarity_subjectivity(sentiment_df, drop_zero_values=False):
    polarities = sentiment_df['polarity'].tolist()
    subjectivities = sentiment_df['subjectivity'].tolist()

    if drop_zero_values == True:
        polarities = list(filter(lambda x: x != 0, polarities))
        subjectivities = list(filter(lambda x: x != 0, subjectivities))

    mean_polarity = sum(polarities)/len(polarities)
    mean_subjectivity = sum(subjectivities)/len(subjectivities)

    return mean_polarity, mean_subjectivity


# ------------------------------------------------------------------------------


def new_df_all_days_sentiment(all_days_folder_path, drop_zero_values=False, clean_tweets=True):
    output_df = pd.DataFrame()
    daily_tweet_folders = os.listdir(all_days_folder_path)
    daily_tweet_folders.sort(reverse=False)
    day_count = 0
    for folder in daily_tweet_folders:
        day_folder_path = os.path.join(all_days_folder_path, folder)
        file_names = os.listdir(day_folder_path)
        file_names.sort()
        file_count = 0
        day_df = pd.DataFrame()
        for file in file_names:
            print(f"processing {file}")
            coin, file_date = get_hashtag_and_date_from_csv_title(file)
            file_path = os.path.join(day_folder_path, file)
            file_df = dataframe_from_tweet_csv(file_path)
            file_df = sentiment_df_from_tweet_df(file_df)

            if drop_zero_values == True:
                file_polarity, file_subjectivity = mean_polarity_subjectivity(
                    file_df, drop_zero_values=True)
            else:
                file_polarity, file_subjectivity = mean_polarity_subjectivity(
                    file_df, drop_zero_values=False)

            if file_count == 0:
                day_sentiment_dict = {
                    'date': [file_date], f'{coin}_polarity': file_polarity, f'{coin}_subjectivity': file_subjectivity}
                day_df = pd.DataFrame(day_sentiment_dict)
            else:
                day_df[f'{coin}_polarity'] = file_polarity
                day_df[f'{coin}_subjectivity'] = file_subjectivity
            file_count += 1
        if day_count == 0:
            output_df = day_df
        else:
            output_df = pd.concat([output_df, day_df], ignore_index=True)
        day_count += 1
    return output_df


# ------------------------------------------------------------------------------

# TODO: modify to take hashtag/filename input and only process those files
# also add option to merge with another file e.g. the shared tweets
# should return an hourly and daily df of sentiment for a hashtag (as collected by scraper)
# can then combine that df with
def sentiment_hourly_and_daily_all(all_days_folder_path):
    # load in date to process from, can make a function to get this date from existing sentiment files
    daily_output_df = pd.DataFrame()
    hourly_output_df = pd.DataFrame()
    daily_tweet_folders = os.listdir(all_days_folder_path)
    daily_tweet_folders.sort(reverse=False)
    day_count = 0
    for folder in daily_tweet_folders:
        day_folder_path = os.path.join(all_days_folder_path, folder)
        file_names = os.listdir(day_folder_path)
        file_names.sort()
        # can add in skip if already processed before here
        file_count = 0
        day_df = pd.DataFrame()
        hourly_df = pd.DataFrame()
        for file in file_names:
            print(f"processing {file}")
            coin, file_date = get_hashtag_and_date_from_csv_title(file)
            file_path = os.path.join(day_folder_path, file)
            file_df = dataframe_from_tweet_csv(file_path, 'created_at')

            file_df_hourly = df_group_by_hour(file_df, 'created_at')
            times = []
            hourly_polarity_zeros = []
            hourly_polarity_no_zeros = []
            hourly_subjectivity_zeros = []
            hourly_subjectivity_no_zeros = []
            file_df = []

            for group, frame in file_df_hourly:
                times.append(group)
                frame = sentiment_df_from_tweet_df(frame)
                hour_polarity_zeros, hour_subjectivity_zeros = mean_polarity_subjectivity(
                    frame, drop_zero_values=False)
                hour_polarity_no_zeros, hour_subjectivity_no_zeros = mean_polarity_subjectivity(
                    frame, drop_zero_values=True)
                hourly_polarity_zeros.append(hour_polarity_zeros)
                hourly_polarity_no_zeros.append(hour_polarity_no_zeros)
                hourly_subjectivity_zeros.append(hour_subjectivity_zeros)
                hourly_subjectivity_no_zeros.append(hour_subjectivity_no_zeros)
                file_df.append(frame)

            # for group, frame in file_df_hourly:
            #     file_df.append(file_df, frame)

            file_df = pd.concat(file_df)
            file_polarity_no_zeros, file_subjectivity_no_zeros = mean_polarity_subjectivity(
                file_df, drop_zero_values=True)
            file_polarity_zeros, file_subjectivity_zeros = mean_polarity_subjectivity(
                file_df, drop_zero_values=True)

            if file_count == 0:
                day_sentiment_dict = {
                    'date': [file_date], f'{coin}_polarity': file_polarity_no_zeros,
                    f'{coin}_subjectivity': file_subjectivity_no_zeros,
                    f'{coin}_polarity_zeros': file_polarity_zeros,
                    f'{coin}_subjectivity_zeros': file_subjectivity_zeros}
                day_df = pd.DataFrame(day_sentiment_dict)

                hourly_sentiment_dict = {
                    'time': times, f'{coin}_polarity': hourly_polarity_no_zeros,
                    f'{coin}_subjectivity': hourly_subjectivity_no_zeros,
                    f'{coin}_polarity_zeros': hourly_polarity_zeros,
                    f'{coin}_subjectivity_zeros': hourly_subjectivity_zeros}
                hourly_df = pd.DataFrame(hourly_sentiment_dict)
            else:
                day_df[f'{coin}_polarity'] = file_polarity_no_zeros
                day_df[f'{coin}_subjectivity'] = file_subjectivity_no_zeros
                day_df[f'{coin}_polarity_zeros'] = file_polarity_zeros
                day_df[f'{coin}_subjectivity_zeros'] = file_subjectivity_zeros

                hourly_df[f'{coin}_polarity'] = hourly_polarity_no_zeros
                hourly_df[f'{coin}_subjectivity'] = hourly_subjectivity_no_zeros
                hourly_df[f'{coin}_polarity_zeros'] = hourly_polarity_zeros
                hourly_df[f'{coin}_subjectivity_zeros'] = hourly_subjectivity_zeros
            file_count += 1
        if day_count == 0:
            daily_output_df = day_df
            hourly_output_df = hourly_df
        else:
            daily_output_df = pd.concat(
                [daily_output_df, day_df], ignore_index=True)
            hourly_output_df = pd.concat(
                [hourly_output_df, hourly_df], ignore_index=True)
        day_count += 1
    return daily_output_df, hourly_output_df


# ------------------------------------------------------------------------------

def df_hashtag_csv_process_daily_hourly(all_days_folder_path, hashtag, merge_hashtag=None, continue_date=None):
    daily_output_df = pd.DataFrame()
    hourly_output_df = pd.DataFrame()
    daily_tweet_folders = os.listdir(all_days_folder_path)
    daily_tweet_folders.sort(reverse=False)
    day_count = 0
    for folder in daily_tweet_folders:
        day_df = pd.DataFrame()         # output df, daily breakdown
        hourly_df = pd.DataFrame()      # output df, hourly breakdown
        hashtag_df = pd.DataFrame()     # df to store original data from files

        # skipping if already processed before (continue date provided)
        if continue_date:
            folder_date = datetime.fromisoformat(folder).date()
            if folder_date <= continue_date:
                continue

        day_folder_path = os.path.join(all_days_folder_path, folder)
        file_names = os.listdir(day_folder_path)
        file_names.sort()
        file_names = np.asarray(file_names)

        # only selecting files which contain the hashtag string (in title)
        hashtag_files = file_names[np.flatnonzero(
            np.char.find(file_names, hashtag) != -1)]

        # if plan to merge files, add those files to those to be processed
        if merge_hashtag:
            merge_files = file_names[np.flatnonzero(
                np.char.find(file_names, merge_hashtag) != -1)]
            hashtag_files = np.append(hashtag_files, merge_files)

        print(hashtag_files)
        if len(hashtag_files) == 0:
            continue

        # merging all the files into a single dataframe (if multiple)
        for file in hashtag_files:
            file_path = os.path.join(day_folder_path, file)
            file_df = dataframe_from_tweet_csv(file_path, 'created_at')
            hashtag_df = hashtag_df.append(file_df)

        # re-sorting by the time column
        # may not be needed as grouper probably handles fine if unsorted...
        # TODO: test removing this later
        hashtag_df = df_sort_datetime_column(hashtag_df, 'created_at')

        # just using this to get the file date
        coin, date = get_hashtag_and_date_from_csv_title(hashtag_files[0])
        print(f"processing {hashtag} from {date}")

        hashtag_df_hourly = df_group_by_hour(hashtag_df, 'created_at')

        times = []
        hourly_polarity_zeros = []
        hourly_polarity_no_zeros = []
        hourly_subjectivity_zeros = []
        hourly_subjectivity_no_zeros = []
        hashtag_df = []
        counts = []

        for group, frame in hashtag_df_hourly:
            times.append(group)
            counts.append(len(frame))
            frame = sentiment_df_from_tweet_df(frame)
            hour_polarity_zeros, hour_subjectivity_zeros = mean_polarity_subjectivity(
                frame, drop_zero_values=False)
            hour_polarity_no_zeros, hour_subjectivity_no_zeros = mean_polarity_subjectivity(
                frame, drop_zero_values=True)
            hourly_polarity_zeros.append(hour_polarity_zeros)
            hourly_polarity_no_zeros.append(hour_polarity_no_zeros)
            hourly_subjectivity_zeros.append(hour_subjectivity_zeros)
            hourly_subjectivity_no_zeros.append(hour_subjectivity_no_zeros)
            hashtag_df.append(frame)

        hashtag_df = pd.concat(hashtag_df)
        file_polarity_no_zeros, file_subjectivity_no_zeros = mean_polarity_subjectivity(
            hashtag_df, drop_zero_values=True)
        file_polarity_zeros, file_subjectivity_zeros = mean_polarity_subjectivity(
            hashtag_df, drop_zero_values=True)

        sum_counts = sum(counts)

        day_sentiment_dict = {
            'date': [date],
            f'{hashtag}_count': sum_counts,
            f'{hashtag}_polarity': file_polarity_no_zeros,
            f'{hashtag}_subjectivity': file_subjectivity_no_zeros,
            f'{hashtag}_polarity_zeros': file_polarity_zeros,
            f'{hashtag}_subjectivity_zeros': file_subjectivity_zeros}
        day_df = pd.DataFrame(day_sentiment_dict)

        hourly_sentiment_dict = {
            'time': times,
            f'{hashtag}_count': counts,
            f'{hashtag}_polarity': hourly_polarity_no_zeros,
            f'{hashtag}_subjectivity': hourly_subjectivity_no_zeros,
            f'{hashtag}_polarity_zeros': hourly_polarity_zeros,
            f'{hashtag}_subjectivity_zeros': hourly_subjectivity_zeros}
        hourly_df = pd.DataFrame(hourly_sentiment_dict)

        if day_count == 0:
            daily_output_df = day_df
            hourly_output_df = hourly_df
        else:
            daily_output_df = pd.concat(
                [daily_output_df, day_df], ignore_index=True)
            hourly_output_df = pd.concat(
                [hourly_output_df, hourly_df], ignore_index=True)
        day_count += 1
    return daily_output_df, hourly_output_df


# ------------------------------------------------------------------------------
# testing
# ------------------------------------------------------------------------------

# trouble_df = new_df_single_day_hourly_tweetcount(trouble_day_folder)


# test_day_folder = os.path.join(csv_master_folder, "2021-03-01")
# test_file = os.path.join(test_day_folder, "2021-03-01-bitcoin-tweets.csv")

# df = dataframe_from_tweet_csv(test_file, "created_at")
# df_sentiment = sentiment_df_from_tweet_df(df)

# print(df_sentiment)

# polarities = df_sentiment['polarity'].tolist()
# print(sum(polarities)/len(polarities))
