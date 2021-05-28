import os
import tweepy
import yaml
import san
import pandas as pd
from datetime import datetime, date, timedelta
import src.twitter_scraper.snscrape_methods as snscrape_methods
import src.twitter_scraper.tweepy_methods as tweepy_methods
import src.tweet_csv_processing.csv_processing_methods as csv_processing
import src.tweet_csv_processing.sentiment_methods as csv_sentiment
import src.combine_data.combine_methods as combine_data


this_folder = os.path.dirname(os.path.abspath(__file__))
today = date.today() - timedelta(2)

folders = []

folder_data = os.path.join(this_folder, "data")
folder_snscrape_temp = os.path.join(folder_data, "snscrape-temp")
folder_snscrape_archive = os.path.join(folder_data, "snscrape-archive")
folder_raw_tweets = os.path.join(folder_data, "tweet-csv-raw")
folder_cleaned_tweets = os.path.join(folder_data, "tweet-csv-cleaned")
folder_processed_tweets = os.path.join(folder_data, "processed-tweet-data")
folder_price_data = os.path.join(folder_data, "price-data")
folder_datasets = os.path.join(os.path.dirname(this_folder), "datasets")

folder_auth = os.path.join(this_folder, "auth")
file_twitter_auth = os.path.join(folder_auth, "twitter-auth.txt")
file_santiment_auth = os.path.join(folder_auth, "santiment-auth.txt")


folders = [folder_data, folder_snscrape_temp, folder_snscrape_archive,
           folder_raw_tweets, folder_cleaned_tweets, folder_processed_tweets,
           folder_price_data, folder_auth, folder_datasets]

for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Loading cryptocurrency settings
yml_cryptocurrencies = os.path.join(this_folder, "cryptocurrencies.yml")
cryptocurrencies = []
with open(yml_cryptocurrencies) as file:
    cryptocurrencies = yaml.full_load(file)

# Loading script settings
yml_settings = os.path.join(this_folder, "settings.yml")
settings = None
with open(yml_settings) as file:
    settings = yaml.full_load(file)

last_tweet_collection = settings["last_tweet_collection"]
last_price_collection = settings["last_price_collection"]
collect_tweets = settings["collect_tweets"]
process_tweets = settings["process_tweets"]
collect_prices = settings["collect_prices"]
create_datasets = settings["create_datasets"]

first_tweet_collection = settings["first_tweet_collection"]


print(f"Today's date is {today}\n")

# ------------------------------------------------------------------------------
# Collecting Twitter Data
# ------------------------------------------------------------------------------

# TODO: place auth strings in another .yml? (will have to be hidden)
# but can put a placeholder there if create a clean release version

auth_strings_twitter = []
with open(file_twitter_auth) as f:
    for line in f:
        auth_strings_twitter = line.split(",")

access_token = auth_strings_twitter[0]
access_token_secret = auth_strings_twitter[1]
consumer_key = auth_strings_twitter[2]
consumer_secret = auth_strings_twitter[3]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


if collect_tweets:
    print("-"*80)
    print("Collecting Tweets")
    print("-"*80)
    if last_tweet_collection == None:
        last_tweet_collection = today - timedelta(1)

    last_tweet_collection = pd.to_datetime(last_tweet_collection).date()

    if last_tweet_collection != today - timedelta(1) and last_tweet_collection != today:
        days_not_run = (today - last_tweet_collection).days
        print(
            f"The collection script has not been run in {days_not_run} days\n")
        print(
            f"The script will now collect data from the past {days_not_run} days\n")
        print("This may take a while")
        print("For more consistent results it is best to run the script every day\n")

    if last_tweet_collection == today:
        print("You have collected tweets already today")

    while last_tweet_collection < today:
        start_date = last_tweet_collection
        end_date = start_date + timedelta(1)
        print(f"Collecting tweets from {start_date} to {end_date}")
        # collect tweets here

        shared_tweet_ids = []
        more_than_one_shared = False

        for coin in cryptocurrencies:
            hashtags = coin["hashtags"]
            # generating snsscrape files
            snscrape_methods.snscrape_tweets_hashtags(
                hashtags, start_date, end_date, folder_snscrape_temp)
            # moving/merging related hashtags snscrape files to same folder
            snscrape_methods.move_snscrape_files(
                folder_snscrape_temp, hashtags[1:], os.path.join(folder_snscrape_temp, hashtags[0]))

            coin_tweet_list = snscrape_methods.snscrape_separate_ids(
                hashtags[0], folder_snscrape_temp)

            coin["tweet_list"] = coin_tweet_list

            if len(shared_tweet_ids) == 0 and coin["filter_shared"] == True:
                shared_tweet_ids = coin_tweet_list
            elif coin["filter_shared"] == True:
                shared_tweet_ids = list(
                    set(shared_tweet_ids).intersection(coin_tweet_list))
                more_than_one_shared = True
            else:
                continue

        print("Totals for each coin:")

        for coin in cryptocurrencies:
            if coin["filter_shared"] == True and more_than_one_shared == True:
                coin["tweet_list"] = list(
                    set(coin["tweet_list"]).difference(shared_tweet_ids))
            print("{0} tweets collected: {1}".format(
                coin["name"], len(coin["tweet_list"])))

        chunk_size = 100

        if more_than_one_shared == True:
            print("shared tweets collected: {0}".format(len(shared_tweet_ids)))
            shared_tweet_csv_name = f"{start_date}-shared-tweets"
            tweepy_methods.get_tweets_and_create_csv(
                api, shared_tweet_ids, chunk_size, folder_raw_tweets, start_date, shared_tweet_csv_name)

        for coin in cryptocurrencies:
            coin_csv_name = "{0}-{1}-tweets".format(start_date, coin["name"])
            tweepy_methods.get_tweets_and_create_csv(
                api, coin["tweet_list"], chunk_size, folder_raw_tweets, start_date, coin_csv_name)
            snscrape_methods.move_snscrape_files(
                folder_snscrape_temp, coin["hashtags"], folder_snscrape_archive)
            # clearing the tweet list
            coin["tweet_list"] = None

        last_tweet_collection = last_tweet_collection + timedelta(1)
        settings["last_tweet_collection"] = str(last_tweet_collection)
        if first_tweet_collection == None:
            first_tweet_collection = str(today)
            settings["first_tweet_collection"] = first_tweet_collection

        with open('settings.yml', 'w') as f:
            data = yaml.dump(settings, f)


# ------------------------------------------------------------------------------
# Processing Twitter Data
# ------------------------------------------------------------------------------
if process_tweets:
    print("-"*80)
    print("Detecting Any badly formatted tweets")
    print("-"*80)
    # Delete Bad Tweets
    csv_processing.delete_bad_tweets_all_csvs_create_new(
        folder_raw_tweets, folder_cleaned_tweets, only_process_new=True)

    print("-"*80)
    print("Performing sentiment and volume analysis on tweets")
    print("-"*80)

    # Sentiment and volume analysis of tweets
    continue_date = None
    processed_filenames = os.listdir(folder_processed_tweets)
    processed_filenames = [
        processed_filenames for processed_filenames in processed_filenames if processed_filenames.endswith(".csv")]

    if len(processed_filenames) != 0:
        first_file = os.path.join(
            folder_processed_tweets, processed_filenames[0])

        continue_date = csv_processing.get_last_date_csv(
            first_file, 'datetime')

    # TODO: might be good to save the sentiment files from each coin/date, incase need to re-run
    # also currently many of the tweets are processed twice, when finding the combined sentiment
    # - would need to restructure function to return/save each sentiment df
    # - would need to implement checks to see if sentiment files already exist if do
    # - appending sentiment scores besides each tweet might be an option
    #   though currently only english non-duplicate text tweets are processed...so may have a lot of null values
    # - This method works for now even if a little inefficent, so low priority...
    # - less modification needed if write to csv in function, or take the logic out of the function
    # - Perhaps wait and see, it may be better to see if the results from merging with shared
    #   and not perform differently in the models

    # default behaviour to merge back in shared files
    for coin in cryptocurrencies:
        daily_path = os.path.join(
            folder_processed_tweets, "{0}_twitter_daily.csv".format(coin["name"]))
        hourly_path = os.path.join(
            folder_processed_tweets, "{0}_twitter_hourly.csv".format(coin["name"]))

        coin_daily = None
        coin_hourly = None
        if coin["filter_shared"] == True:
            coin_daily, coin_hourly = csv_sentiment.df_hashtag_csv_process_daily_hourly(
                folder_cleaned_tweets, coin["name"], merge_hashtag="shared", continue_date=continue_date)
        else:
            coin_daily, coin_hourly = csv_sentiment.df_hashtag_csv_process_daily_hourly(
                folder_cleaned_tweets, coin["name"], continue_date=continue_date)

        if continue_date:
            coin_hourly.to_csv(hourly_path, index=False,
                               header=False, mode='a')
            coin_daily.to_csv(daily_path, index=False,
                              header=False, mode='a')
        else:
            coin_hourly.to_csv(hourly_path, index=False,
                               header=True, mode='w+')
            coin_daily.to_csv(daily_path, index=False,
                              header=True, mode='w+')

    # creating data without shared tweets (to see if performs better in ML models)
    for coin in cryptocurrencies:
        if coin["filter_shared"] == False:
            continue
        daily_path = os.path.join(
            folder_processed_tweets, "no-shared", "{0}_twitter_no_shared_daily.csv".format(coin["name"]))
        hourly_path = os.path.join(
            folder_processed_tweets, "no-shared", "{0}_twitter_no_shared_hourly.csv".format(coin["name"]))

        coin_daily, coin_hourly = csv_sentiment.df_hashtag_csv_process_daily_hourly(
            folder_cleaned_tweets, coin["name"], continue_date=continue_date)

        if continue_date:
            coin_hourly.to_csv(hourly_path, index=False,
                               header=False, mode='a')
            coin_daily.to_csv(daily_path, index=False, header=False, mode='a')
        else:
            coin_hourly.to_csv(hourly_path, index=False,
                               header=True, mode='w+')
            coin_daily.to_csv(daily_path, index=False, header=True, mode='w+')


# ------------------------------------------------------------------------------
# Collecting Price Data
# ------------------------------------------------------------------------------

# TODO: make most of this methods and move to appropriate folder

# Setting up santiment api key (though not sure it's used)
auth_string = ''    # can remove below and provide key here directly
with open(file_santiment_auth) as f:
    for line in f:
        auth_string = line

if collect_prices:
    print("-"*80)
    print("Collecting Price Data")
    print("-"*80)
    start_date = last_price_collection
    first_run = False
    if start_date == None:
        first_run = True
        if first_tweet_collection != None:
            start_date = pd.to_datetime(first_tweet_collection).date()
            start_date = str(start_date - timedelta(1))
        else:
            start_date = str(today - timedelta(1))

    # santiment API start and end dates are inclusive
    end_date = str(today - timedelta(1))
    write_date = str(today)
    if datetime.strptime(start_date, '%Y-%m-%d') > datetime.strptime(end_date, '%Y-%m-%d'):
        print("oh no")
        print(f"it seems you have already collected prices up to {end_date}")
        print("to override change the date in settings.yml")
    else:
        print(f"Collecting Price data from {start_date} to {write_date}")

        # fetching hourly data from santiment API
        for coin in cryptocurrencies:
            query = "ohlcv/" + coin["name"]
            print("fetching hourly price data for {0}".format(coin["name"]))
            ohlcv_hourly_df = san.get(
                query,
                from_date=start_date,
                to_date=end_date,
                interval="1h"
            )

            if first_run:
                csv_path = os.path.join(
                    folder_price_data, "{0}_prices_hourly.csv".format(coin["name"]))
                ohlcv_hourly_df.to_csv(csv_path, index=True,
                                       header=True, mode='w+')
            else:
                csv_path = os.path.join(
                    folder_price_data, "{0}_prices_hourly.csv".format(coin["name"]))
                ohlcv_hourly_df.to_csv(csv_path, index=True,
                                       header=False, mode='a')

        # fetching daily data from santiment api
        for coin in cryptocurrencies:
            query = "ohlcv/" + coin["name"]
            print("fetching daily price data for {0}".format(coin["name"]))
            ohlcv_daily_df = san.get(
                query,
                from_date=start_date,
                to_date=end_date,
                interval="1d"
            )
            if first_run:
                csv_path = os.path.join(
                    folder_price_data, "{0}_prices_daily.csv".format(coin["name"]))
                ohlcv_daily_df.to_csv(
                    csv_path, index=True, header=True, mode='w+')
            else:
                csv_path = os.path.join(
                    folder_price_data, "{0}_prices_daily.csv".format(coin["name"]))
                ohlcv_daily_df.to_csv(
                    csv_path, index=True, header=False, mode='a')

        settings["last_price_collection"] = write_date

        with open('settings.yml', 'w') as f:
            data = yaml.dump(settings, f)

# ------------------------------------------------------------------------------
# Creating datasets
# ------------------------------------------------------------------------------

if create_datasets:
    print("-"*80)
    print("Creating Datasets")
    print("-"*80)

    price_files = os.listdir(folder_price_data)
    tweet_files = os.listdir(folder_processed_tweets)
    tweet_files_no_shared = os.listdir(
        os.path.join(folder_processed_tweets, "no-shared"))

    hourly_price_files = [
        price_files for price_files in price_files if price_files.endswith("hourly.csv")]

    hourly_tweet_files = [
        tweet_files for tweet_files in tweet_files if tweet_files.endswith("hourly.csv")]

    cryptocurrencies = ["ethereum", "dogecoin", "bitcoin"]

    for coin in cryptocurrencies:
        price_file = [
            hourly_price_files for hourly_price_files in hourly_price_files if hourly_price_files.startswith(coin)][0]
        tweet_file = [
            hourly_tweet_files for hourly_tweet_files in hourly_tweet_files if hourly_tweet_files.startswith(coin)][0]

        price_path = os.path.join(folder_price_data, price_file)
        tweet_path = os.path.join(folder_processed_tweets, tweet_file)

        output_csv = os.path.join(
            folder_datasets, "{0}_hourly.csv".format(coin))

        combine_data.merge_processed_hourly_data(
            price_path, tweet_path, output_csv)
