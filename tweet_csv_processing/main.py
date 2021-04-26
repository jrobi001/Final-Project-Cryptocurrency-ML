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

hashtags = ["ethereum", "bitcoin", "dogecoin"]

# TODO: change csv mode to 'a' and create check for if file exists (and w+ then)
# then add in code for checking date after running today and see if can successfully
# append sentiments to tomorrows

# this is running without shared tweets merged to bitcoin and ethereum
for hashtag in hashtags:
    daily_path = os.path.join(
        output_csv_folder, "without-shared", f"{hashtag}_daily.csv")
    hourly_path = os.path.join(
        output_csv_folder, "without-shared", f"{hashtag}_hourly.csv")
    hashtag_daily, hashtag_hourly = sentiment.df_hashtag_csv_process_daily_hourly(
        cleaned_csv_master_folder, hashtag)

    hashtag_hourly.to_csv(hourly_path, index=False, header=True, mode='w+')
    hashtag_daily.to_csv(daily_path, index=False, header=True, mode='w+')

# this is running with shared tweets merged to bitcoin and ethereum
for hashtag in hashtags:
    daily_path = os.path.join(
        output_csv_folder, "with-shared", f"{hashtag}_daily.csv")
    hourly_path = os.path.join(
        output_csv_folder, "with-shared", f"{hashtag}_hourly.csv")
    if hashtag == "dogecoin":
        hashtag_hourly, hashtag_daily = sentiment.df_hashtag_csv_process_daily_hourly(
            cleaned_csv_master_folder, hashtag)
    else:
        hashtag_hourly, hashtag_daily = sentiment.df_hashtag_csv_process_daily_hourly(
            cleaned_csv_master_folder, hashtag, merge_hashtag="shared")

    hashtag_hourly.to_csv(hourly_path, index=False, header=True, mode='w+')
    hashtag_daily.to_csv(daily_path, index=False, header=True, mode='w+')


# # -------------------------------------------------------------------------------
# # Tweet Volume - Hourly Breakdown
# # -------------------------------------------------------------------------------

# tweet_volume_hourly_csv = os.path.join(
#     output_csv_folder, "tweet-volume-hourly.csv")
# df = processing.new_df_all_days_hourly_tweetcount(cleaned_csv_master_folder)
# df.to_csv(tweet_volume_hourly_csv, index=False, header=True, mode='w+')


# # -------------------------------------------------------------------------------
# # Tweet Sentiment - Daily Breakdown
# # -------------------------------------------------------------------------------

# daily_sentiment_df, hourly_sentiment_df = sentiment.sentiment_hourly_and_daily_all(
#     cleaned_csv_master_folder)

# daily_sentiment_path = os.path.join(
#     output_csv_folder, "tweet-sentiment-daily.csv")

# hourly_sentiment_path = os.path.join(
#     output_csv_folder, "tweet-sentiment-hourly.csv")

# daily_sentiment_df.to_csv(
#     daily_sentiment_path, index=False, header=True, mode='w+')

# hourly_sentiment_df.to_csv(
#     hourly_sentiment_path, index=False, header=True, mode='w+')
