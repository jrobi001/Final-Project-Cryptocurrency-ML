import os
import tweepy
import yaml
import san
from datetime import datetime, date, timedelta
import src.twitter_scraper.snscrape_methods as snscrape_methods
import src.twitter_scraper.tweepy_methods as tweepy_methods
import src.tweet_csv_processing.csv_processing_methods as csv_processing
import src.tweet_csv_processing.sentiment_methods as csv_sentiment

# TODO: either make checks that folders exist, or put a placeholder.txt or
# readme in each folder so that they exist on the git.

this_folder = os.path.dirname(os.path.abspath(__file__))

folder_data = os.path.join(this_folder, "data")
folder_snscrape_temp = os.path.join(folder_data, "snscrape-temp")
folder_snscrape_archive = os.path.join(folder_data, "snscrape-archive")
folder_raw_tweets = os.path.join(folder_data, "tweet-csv-raw")
folder_cleaned_tweets = os.path.join(folder_data, "tweet-csv-cleaned")
folder_processed_tweets = os.path.join(folder_data, "processed-tweet-data")
folder_price_data = os.path.join(folder_data, "price-data")

folder_auth = os.path.join(this_folder, "auth")
file_twitter_auth = os.path.join(folder_auth, "twitter-auth.txt")
file_santiment_auth = os.path.join(folder_auth, "santiment-auth.txt")

# Loading settings
yml_cryptocurrencies = os.path.join(this_folder, "cryptocurrencies.yml")
cryptocurrencies = []
with open(yml_cryptocurrencies) as file:
    cryptocurrencies = yaml.full_load(file)

# TODO: I think moving all the logic to main functions in src makes sense
# only perform setup and calls to the main functions here

# TODO: move data integrity/testing functions to their own folder
# create set of functions to check days data and all data

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

# TODO: save a last run date and adjust the start date accordingly (rather than always the day before)
# also if multiple dates will need to loop (may be best to create function to collect single date tweets)
end_date = date.today()  # TODO: move these as setup parameters in settings
start_date = end_date - timedelta(1)
print("Today's date:", end_date)
print("Collecting tweets from:", start_date)

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
    # clearing the tweet list (not-needed again)
    coin["tweet_list"] = None

# ------------------------------------------------------------------------------
# Processing Twitter Data
# ------------------------------------------------------------------------------

# Delete Bad Tweets
csv_processing.delete_bad_tweets_all_csvs_create_new(
    folder_raw_tweets, folder_cleaned_tweets, only_process_new=True)

# Sentiment and volume analysis of tweets
continue_date = None
processed_filenames = os.listdir(folder_processed_tweets)
processed_filenames = [
    processed_filenames for processed_filenames in processed_filenames if processed_filenames.endswith(".csv")]

if len(processed_filenames) != 0:
    first_file = os.path.join(folder_processed_tweets, processed_filenames[0])

    continue_date = csv_processing.get_last_date_csv(first_file, 'datetime')

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

# creating data without shared tweets (to see if performs better)
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
        coin_hourly.to_csv(hourly_path, index=False, header=False, mode='a')
        coin_daily.to_csv(daily_path, index=False, header=False, mode='a')
    else:
        coin_hourly.to_csv(hourly_path, index=False, header=True, mode='w+')
        coin_daily.to_csv(daily_path, index=False, header=True, mode='w+')


# ------------------------------------------------------------------------------
# Collecting Price Data
# ------------------------------------------------------------------------------

# TODO: make most of this methods and move to appropriate folder

price_start_date_file = os.path.join(this_folder, 'start-date.txt')

first_run = False

# Setting up santiment api key (is single string stored in auth.txt)
auth_string = ''    # can remove below and provide key here directly
with open(file_santiment_auth) as f:
    for line in f:
        auth_string = line


end_date = date.today()         # TODO: remove
# santiment dates are inclusive (unlike snscrape)
# collecting prices only up to midnight last night (as is same period tweets currently collected to)
price_end_date = str(end_date - timedelta(1))
# TODO: replace this with a setting, like collection period start or something
# or detect it from the first date in the twitter data
price_start_date = "2021-01-31"


if not os.path.exists(price_start_date_file):
    first_run = True
else:
    with open(price_start_date_file) as f:
        for line in f:
            price_start_date = line


if datetime.strptime(price_start_date, '%Y-%m-%d') > datetime.strptime(price_end_date, '%Y-%m-%d'):
    print("oh no")
    print(f"it seems you have already collected prices up to {price_end_date}")
    print("to override change the date in price_collection/start-date.txt")

else:
    print(f"collecting prices between {price_start_date} and {price_end_date}")

    # fetching hourly data from santiment API
    for coin in cryptocurrencies:
        query = "ohlcv/" + coin["name"]
        print("fetching hourly price data for {0}".format(coin["name"]))
        ohlcv_hourly_df = san.get(
            query,
            from_date=price_start_date,
            to_date=price_end_date,
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
            from_date=price_start_date,
            to_date=price_end_date,
            interval="1d"
        )
        if first_run:
            csv_path = os.path.join(
                folder_price_data, "{0}_prices_daily.csv".format(coin["name"]))
            ohlcv_daily_df.to_csv(csv_path, index=True, header=True, mode='w+')
        else:
            csv_path = os.path.join(
                folder_price_data, "{0}_prices_daily.csv".format(coin["name"]))
            ohlcv_daily_df.to_csv(csv_path, index=True, header=False, mode='a')


# the day after the end date of price collection (same as snscrape end date)
write_date = str(end_date)
f = open(price_start_date_file, "w")
f.write(write_date)
f.close()
