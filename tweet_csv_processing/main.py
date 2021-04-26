import os
import src.csv_processing_methods as processing
import src.sentiment_methods as sentiment

this_folder = os.path.dirname(os.path.abspath(__file__))

original_csv_master_folder = os.path.join(os.path.dirname(
    this_folder), "twitter_scraper", "csv-tweet-files")

cleaned_csv_master_folder = os.path.join(
    os.path.dirname(this_folder), "tweet-csv-cleaned")

output_csv_folder = os.path.join(
    os.path.dirname(this_folder), "processed-tweet-data")

# -------------------------------------------------------------------------------
# Delete Bad Tweets
# -------------------------------------------------------------------------------

processing.delete_bad_tweets_all_csvs_create_new(
    original_csv_master_folder, cleaned_csv_master_folder, only_process_new=True)

# -------------------------------------------------------------------------------
# Tweet Volume - Hourly Breakdown
# -------------------------------------------------------------------------------

tweet_volume_hourly_csv = os.path.join(
    output_csv_folder, "tweet-volume-hourly.csv")
df = processing.new_df_all_days_hourly_tweetcount(cleaned_csv_master_folder)
df.to_csv(tweet_volume_hourly_csv, index=False, header=True, mode='w+')


# -------------------------------------------------------------------------------
# Tweet Sentiment - Daily Breakdown
# -------------------------------------------------------------------------------

daily_sentiment_df, hourly_sentiment_df = sentiment.sentiment_hourly_and_daily_all(
    cleaned_csv_master_folder)

daily_sentiment_path = os.path.join(
    output_csv_folder, "tweet-sentiment-daily.csv")

hourly_sentiment_path = os.path.join(
    output_csv_folder, "tweet-sentiment-hourly.csv")

daily_sentiment_df.to_csv(
    daily_sentiment_path, index=False, header=True, mode='w+')

hourly_sentiment_df.to_csv(
    hourly_sentiment_path, index=False, header=True, mode='w+')


# tweet_sentiment_daily_no_zero = os.path.join(
#     output_csv_folder, "tweet-sentiment-daily-no-zero.csv")

# daily_sentiment_df = sentiment.new_df_all_days_sentiment(
#     cleaned_csv_master_folder, drop_zero_values=True)

# daily_sentiment_df.to_csv(
#     tweet_sentiment_daily_no_zero, index=False, header=True, mode='w+')


# tweet_sentiment_daily_with_zeros = os.path.join(
#     output_csv_folder, "tweet-sentiment-daily-with-zeros.csv")

# daily_sentiment_df = sentiment.new_df_all_days_sentiment(
#     cleaned_csv_master_folder, drop_zero_values=False)

# daily_sentiment_df.to_csv(
#     tweet_sentiment_daily_with_zeros, index=False, header=True, mode='w+')
