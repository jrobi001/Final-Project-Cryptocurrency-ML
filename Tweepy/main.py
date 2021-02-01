import tweepy
import os
from datetime import date, timedelta
from snscrape_methods import snscrape_tweets_hashtags, snscrape_separate_ids
from tweepy_methods import get_tweets_and_create_csv

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
hashtags = ["bitcoin", "ethereum"]

today = date.today()
yesterday = today - timedelta(1)
print("Today's date:", today)
print("Collecting tweets from:", yesterday)

snscrape_temp_folder = this_folder + "/snscrape-temp/"

snscrape_tweets_hashtags(hashtags, yesterday, today, snscrape_temp_folder)
bitcoin_tweet_ids = snscrape_separate_ids(hashtags[0], snscrape_temp_folder)
ethereum_tweet_ids = snscrape_separate_ids(hashtags[1], snscrape_temp_folder)

# seperating out duplicated tweets, to reduce API calls-------------------------
shared_tweet_ids = list(
    set(bitcoin_tweet_ids).intersection(ethereum_tweet_ids))

bitcoin_tweet_ids = list(set(bitcoin_tweet_ids).difference(shared_tweet_ids))
ethereum_tweet_ids = list(set(ethereum_tweet_ids).difference(shared_tweet_ids))

print(f"{len(shared_tweet_ids)} shared tweets found between tweet id lists")
print("tweet list totals: bitcoin = {0}, ethereum = {1}, shared = {2}".format(
    len(bitcoin_tweet_ids), len(ethereum_tweet_ids), len(shared_tweet_ids)
))

# calling api and exporting to csv----------------------------------------------
chunk_size = 100

shared_tweet_csv_name = f"{yesterday}-shared-tweets"
get_tweets_and_create_csv(api, shared_tweet_ids, chunk_size,
                          this_folder, shared_tweet_csv_name)

bitcoin_tweet_csv_name = f"{yesterday}-bitcoin-tweets"
get_tweets_and_create_csv(api, bitcoin_tweet_ids, chunk_size,
                          this_folder, bitcoin_tweet_csv_name)

ethereum_tweet_csv_name = f"{yesterday}-ethereum-tweets"
get_tweets_and_create_csv(api, ethereum_tweet_ids, chunk_size,
                          this_folder, ethereum_tweet_csv_name)
