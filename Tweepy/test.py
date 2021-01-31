import tweepy
import os
import csv
import pandas as pd
from datetime import date

this_folder = os.path.dirname(os.path.abspath(__file__))
auth_file = os.path.join(this_folder, 'auth.txt')


auth_strings = []
with open(auth_file) as f:
    for line in f:
        auth_strings = line.split(",")

access_token = auth_strings[0]
access_token_secret = auth_strings[1]
consumer_key = auth_strings[2]
consumer_secret = auth_strings[3]


# print(auth_strings)
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

search_term = "#bitcoin"
today = date.today()
print("Today's date:", today)

# id_str	from_user	text	created_at	time	geo_coordinates	user_lang	in_reply_to_user_id_str	in_reply_to_screen_name	from_user_id_str	in_reply_to_status_id_str	source	profile_image_url	user_followers_count	user_friends_count	user_location	status_url	entities_str

# plan is to use the snscrape method.
# create commands to use snscrape to get tweet lists for each coin the day before
# extract id's and convert to dictionary to filter out any duplicates
# use tweepy statuses_lookup() to look at batches of those tweets (100 at a time)
# to df then to csv


tweets = tweepy.Cursor(api.search, q=search_term,
                       lang="en", since=today).items(5)


# with open(today+"-bitcoin.csv", 'a+', newline='') as csv_file:

# public_tweets = api.home_timeline()
# for tweet in public_tweets:
#     print(tweet)
