import os
import src.combine_data.combine_methods as combine_data

this_folder = os.path.dirname(os.path.abspath(__file__))
folder_data = os.path.join(this_folder, "data")
folder_processed_tweets = os.path.join(folder_data, "processed-tweet-data")
folder_price_data = os.path.join(folder_data, "price-data")

folder_datasets = os.path.join(os.path.dirname(this_folder), "datasets")

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

    output_csv = os.path.join(folder_datasets, "{0}_hourly.csv".format(coin))

    combine_data.merge_processed_hourly_data(
        price_path, tweet_path, output_csv)
