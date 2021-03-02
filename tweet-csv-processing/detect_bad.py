import pandas as pd
import time
import os
from datetime import date, datetime, timedelta
import csv

# TODO's:
# - Rename file, create docstrings, add comments, maybe rework method titles
# - possibly re-locate these methods to the collection process so that they are performed
#  when tweets are collected. Keep only analysis processing here?
# - Would Ideally like everything to run off of a single script

# -------------------------------------------------------------------------------
# Methods
# -------------------------------------------------------------------------------


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

# -------------------------------------------------------------------------------


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

# -------------------------------------------------------------------------------


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

# -------------------------------------------------------------------------------


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

# -------------------------------------------------------------------------------
# Calls
# -------------------------------------------------------------------------------


this_folder = os.path.dirname(os.path.abspath(__file__))
original_master = os.path.join(os.path.dirname(
    this_folder), "twitter-scraper", "csv-tweet-files")
print(original_master)
# input_master = os.path.join(this_folder, "input-csv")

output_master = os.path.join(os.path.dirname(this_folder), "tweet-csv-cleaned")

delete_bad_tweets_all_csvs_create_new(
    original_master, output_master, only_process_new=True)
