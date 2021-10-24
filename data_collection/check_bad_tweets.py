import src.tweet_csv_processing.csv_processing_methods as csv_processing
import os

this_folder = os.path.dirname(os.path.abspath(__file__))

folder_data = os.path.join(this_folder, "data")
folder_raw_tweets = os.path.join(folder_data, "tweet-csv-raw")


csv_processing.print_bad_tweets_all_csvs(folder_raw_tweets)
# csv_processing.print_indexes_of_bad_format_tweets(bad_file)
