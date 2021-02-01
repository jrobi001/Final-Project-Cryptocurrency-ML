import tweepy
import os
import csv
import pandas as pd
from datetime import date, timedelta
from snscrape_methods import snscrape_tweets_hashtags, snscrape_separate_ids

this_folder = os.path.dirname(os.path.abspath(__file__))
auth_file = os.path.join(this_folder, 'auth.txt')

# Setting up Tweepy auth from strings stored in file ---------------------------
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

api = tweepy.API(auth)
# -------------------------------------------------------------------------------

this_folder = os.path.dirname(os.path.abspath(__file__))

hashtags = ["bitcoin", "ethereum"]

today = date.today()
yesterday = today - timedelta(1)
# print("Today's date:", today)
# print("Collecting tweets from:", yesterday)

snscrape_temp_folder = this_folder + "/snscrape-temp/"

# snscrape_tweets_hashtags(hashtags, yesterday, today, snscrape_temp_folder)
bitcoin_tweet_ids = snscrape_separate_ids(hashtags[0], snscrape_temp_folder)
ethereum_tweet_ids = snscrape_separate_ids(hashtags[1], snscrape_temp_folder)

status = api.statuses_lookup(
    [ethereum_tweet_ids[1]], tweet_mode="extended")
status = status[0]


hashtags_string = ""
entities_hashtag = status.entities['hashtags']
for i in range(len(entities_hashtag)):
    hashtags_string = hashtags_string + "#" + entities_hashtag[i]['text']


print(hashtags_string)

tweet = {
    "id_str": str(status.id_str),
    "from_user": status.user.name,
    "text": status.full_text.replace('\n', ' '),
    "created_at": str(status.created_at),
    # "time": null,
    "geo_coordinates": status.coordinates,
    "user_lang": status.lang,
    # "in_reply_to_user_id_str": null,
    # "in_reply_to_screen_name": null,
    "from_user_id_str": str(status.user.id_str),
    "in_reply_to_status_id_str": str(status.in_reply_to_status_id_str),
    # "source": null,
    # "profile_image_url": null,
    "user_followers_count": str(status.user.followers_count),
    # "user_friends_count": null,
    "user_location": str(status.user.location),
    # "status_url": null,
    # "entities_str": null,
    # NOTE:Additional column to TAGS
    "hashtags": hashtags_string
}
print(tweet)
