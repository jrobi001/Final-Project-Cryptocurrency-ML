import os
import src.tweet_csv_processing.csv_processing_methods as csv_processing

this_folder = os.path.dirname(os.path.abspath(__file__))

data_folder = os.path.join(this_folder, "data")
snscrape_temp = os.path.join(data_folder, "snscrape-temp")
snscrape_archive = os.path.join(data_folder, "snscrape-archive")
raw_tweet_folder = os.path.join(data_folder, "tweet-csv-raw")
cleaned_tweet_folder = os.path.join(data_folder, "tweet-csv-cleaned")
processed_tweet_folder = os.path.join(data_folder, "processed-tweet-data")
price_data_folder = os.path.join(data_folder, "price_data")

auth_folder = os.path.join(this_folder, "auth")
twitter_auth = os.path.join(auth_folder, "twitter-auth.txt")

# TODO: either make checks that folders exist, or put a placeholder.txt or
# readme in each folder so that they exist on the git.
