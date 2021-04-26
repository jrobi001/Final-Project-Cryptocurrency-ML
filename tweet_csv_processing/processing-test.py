# %%
import numpy as np
import pandas as pd
import time
import os
from datetime import date, datetime, timedelta

import src.csv_processing_methods as processing
import src.sentiment_methods as sentiment

# TODO: Things to test:
# - order of date folders when processing
# - getting the end date from a processed analysis CSV
# - if can use that end date to skip over folders by converting them to date objects
# -

this_folder = os.path.dirname(os.path.abspath(__file__))

original_csv_master_folder = os.path.join(os.path.dirname(
    this_folder), "twitter_scraper", "csv-tweet-files")

cleaned_csv_master_folder = os.path.join(
    os.path.dirname(this_folder), "tweet-csv-cleaned")

output_csv_folder = os.path.join(
    os.path.dirname(this_folder), "processed-tweet-data")


# %%
df_dates = test_file_df['time'].dt.date
print(df_dates)

# %%
print(df_dates.max() + timedelta(1))

# %%
test_file_df["time"].dt.date.max() + timedelta(1)

# %%


def get_last_date_csv(csv_file_path, time_column):
    # TODO: might need to handle empty file, or non-existent files
    file_df = processing.dataframe_from_tweet_csv(csv_file_path, time_column)
    # could be rewritten as a single step, but
    date = file_df[time_column].dt.date.max()
    return date


continue_date = get_last_date_csv(test_file, "time")

# %%
daily_tweet_folders = os.listdir(original_csv_master_folder)
daily_tweet_folders.sort(reverse=False)

for folder in daily_tweet_folders:
    folder_date = datetime.fromisoformat(folder).date()
    if folder_date <= continue_date:
        continue

    print(folder_date)

# %%
test_folder = os.path.join(cleaned_csv_master_folder, "2021-04-13")
file_names = os.listdir(test_folder)
file_names = np.asarray(file_names)

# source: https://stackoverflow.com/questions/38974168/finding-entries-containing-a-substring-in-a-numpy-array
hashtag_files = file_names[np.flatnonzero(
    np.char.find(file_names, "bitcoin") != -1)]

hashtag_df = pd.DataFrame()

# file_path = os.path.join(test_folder, hashtag_files[0])
# file_df = processing.dataframe_from_tweet_csv(file_path, 'created_at')

for file in hashtag_files:
    file_path = os.path.join(test_folder, file)
    file_df = processing.dataframe_from_tweet_csv(file_path, 'created_at')
    print(file_df)
    hashtag_df = hashtag_df.append(file_df)

print(hashtag_df)

# %%
# test merging two dfs together
sent_path = os.path.join(output_csv_folder, "tweet-sentiment-hourly.csv")
vol_path = os.path.join(output_csv_folder, "tweet-volume-hourly.csv")

sent_df = processing.dataframe_from_tweet_csv(sent_path)
vol_df = processing.dataframe_from_tweet_csv(vol_path)

vol_df = vol_df.drop(['Time'], axis=1)

out_df = pd.concat([sent_df, vol_df], axis=1)
print(out_df)

# %%
counts = [100, 200, 300]
print(sum(counts))

# %%

daily, hourly = sentiment.df_hashtag_csv_process_daily_hourly(
    cleaned_csv_master_folder, "ethereum", merge_hashtag="shared")

daily.to_csv(
    output_csv_folder + "/test_eth_daily.csv", index=False, header=True, mode='w+')


hourly.to_csv(
    output_csv_folder + "/test_eth_hourly.csv", index=False, header=True, mode='w+')


# %%
os.path.join(output_csv_folder, "abs", f"abc_daily.csv")

# for file in file_names:
#     if "ethereum" in file:
#         print(file)

# current_folder = os.path.dirname(os.path.abspath(__file__))
# test_csv = os.path.join(current_folder, 'input-csv',
#                         '2021-02-11-ethereum-tweets.csv')

# example_time = "2021-02-11 23:01:43"
# date, time = example_time.split(' ')
# date_time = datetime.fromisoformat(example_time)
# date, time = date_time.date(), date_time.time()
# file_date = datetime.fromisoformat("2021-02-11").date()
# print(file_date)


# df = pd.read_csv(
#     test_csv)  # , dtype='string', chunksize=4000, low_memory=False)

# # print(df.iloc[0])

# df['created_at'] = pd.to_datetime(df['created_at'])
# df = df.set_index(df['created_at'])
# df = df.sort_index()

# # -------------------------------------------------------------------------------
# # method of grouping tweets by hour
# # https://realpython.com/pandas-groupby/#how-pandas-groupby-works
# df_hourly = df.groupby(pd.Grouper(key="created_at", freq='H'))

# # methods of iterating over grouped tweets by hour
# for group, frame in df_hourly:
#     print(group)
#     print(len(frame))

# hour, frame = next(iter(df_hourly))
# print(hour)
# print(frame.head(3))
# # -------------------------------------------------------------------------------

# one method of making sure all entries have the right date.
# for index, row in df.iterrows():
#     print(row[3])
#     date_time = datetime.fromisoformat(row[3])
#     print(date_time)
#     date, time = date_time.date(), date_time.time()
#     if date != file_date:
#         print(date)

# %%
