import tweepy
import os
from datetime import date, timedelta
from src.snscrape_methods import snscrape_tweets_hashtags, snscrape_separate_ids, move_snscrape_files
from src.tweepy_methods import get_tweets_and_create_csv

# TODO's:
# - Rename folder to something better                                           [y]
# - integrate in the CSV checks to the end of this script                       [n] - decided better to keep seperate
# - add comments, docstrings etc                                                []
# - re-parameterise some methods and reduce the number of calls required here   []
# ideally only need the settings and 2-3 calls in this script
# - investigate the 'bad' tweets (in test.py) and work out if there is a way    []
# to eliminate them at collection time


# Adapted from:
# https://github.com/cedoard/snscrape_twitter
# https://github.com/HateDetector/scrape-twitter

this_folder = os.path.dirname(os.path.abspath(__file__))

# Setting up Tweepy auth from strings stored in file----------------------------
auth_file = os.path.join(this_folder, 'auth.txt')
auth_strings = []
with open(auth_file) as f:
    for line in f:
        auth_strings = line.split(",")

access_token = auth_strings[0]
access_token_secret = auth_strings[1]
consumer_key = auth_strings[2]
consumer_secret = auth_strings[3]

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


# snscrape tweet id gathering---------------------------------------------------

today = date.today()
yesterday = today - timedelta(1)
print("Today's date:", today)
print("Collecting tweets from:", yesterday)

hashtags = ["ethereum", "eth", "btc", "bitcoin", "dogecoin", "doge"]
snscrape_temp_folder = os.path.join(this_folder, "snscrape-temp")

# generating snsscrape files
snscrape_tweets_hashtags(hashtags, yesterday, today, snscrape_temp_folder)

# moving/mergin related hashtags snscrape files to same folder
move_snscrape_files(snscrape_temp_folder, ["btc"], os.path.join(
    snscrape_temp_folder, "bitcoin"))
move_snscrape_files(snscrape_temp_folder, ["eth"], os.path.join(
    snscrape_temp_folder, "ethereum"))
move_snscrape_files(snscrape_temp_folder, ["doge"], os.path.join(
    snscrape_temp_folder, "dogecoin"))

bitcoin_tweet_ids = snscrape_separate_ids("bitcoin", snscrape_temp_folder)
ethereum_tweet_ids = snscrape_separate_ids("ethereum", snscrape_temp_folder)
dogecoin_tweet_ids = snscrape_separate_ids("dogecoin", snscrape_temp_folder)

# seperating out duplicated tweets, to reduce API calls-------------------------
shared_tweet_ids = list(
    set(bitcoin_tweet_ids).intersection(ethereum_tweet_ids))

bitcoin_tweet_ids = list(set(bitcoin_tweet_ids).difference(shared_tweet_ids))
ethereum_tweet_ids = list(set(ethereum_tweet_ids).difference(shared_tweet_ids))

print(f"{len(shared_tweet_ids)} shared tweets found between tweet id lists")
print("tweet list totals: bitcoin = {0}, ethereum = {1}, shared = {2}".format(
    len(bitcoin_tweet_ids), len(ethereum_tweet_ids), len(shared_tweet_ids)
))
print(f"dogecoin tweets collected: {len(dogecoin_tweet_ids)}")

# calling api and exporting to csv----------------------------------------------
chunk_size = 100

shared_tweet_csv_name = f"{yesterday}-shared-tweets"
get_tweets_and_create_csv(api, shared_tweet_ids, chunk_size,
                          this_folder, yesterday, shared_tweet_csv_name)

bitcoin_tweet_csv_name = f"{yesterday}-bitcoin-tweets"
get_tweets_and_create_csv(api, bitcoin_tweet_ids, chunk_size,
                          this_folder, yesterday, bitcoin_tweet_csv_name)

ethereum_tweet_csv_name = f"{yesterday}-ethereum-tweets"
get_tweets_and_create_csv(api, ethereum_tweet_ids, chunk_size,
                          this_folder, yesterday, ethereum_tweet_csv_name)

dogecoin_tweet_csv_name = f"{yesterday}-dogecoin-tweets"
get_tweets_and_create_csv(api, dogecoin_tweet_ids, chunk_size,
                          this_folder, yesterday, dogecoin_tweet_csv_name)

# archiving the temp snscrape files---------------------------------------------
# so they aren't run the next day

snscrape_archive_folder = os.path.join(this_folder, "snscrape-archive")

move_snscrape_files(snscrape_temp_folder, hashtags,
                    snscrape_archive_folder)
