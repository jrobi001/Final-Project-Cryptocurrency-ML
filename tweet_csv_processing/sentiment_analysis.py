from tweepy_csv_process import *
import pandas as pd
import os
import re
from textblob import TextBlob


def clean_text(text, remove_mentions=True, remove_hashtags=True, remove_links=True, filter_alphanumeric=True):
    cleaned = ""
    for word in text.split():
        if len(word) < 1:
            continue
        elif word[0] == '@' and remove_mentions:
            continue
        elif word[0] == '#' and remove_hashtags:
            continue
        elif word[0:8] == "https://" and remove_links:
            continue
        else:
            cleaned = cleaned + ' ' + word
    if filter_alphanumeric:
        cleaned = re.sub(r'\W+', ' ', cleaned)
    return cleaned


def sentiment_df_from_tweet_df(tweet_dataframe, clean_tweets=True):
    # only english tweets:
    tweet_dataframe = tweet_dataframe.loc[tweet_dataframe["user_lang"] == "en"]
    # drop all columns other than text:
    tweet_dataframe = tweet_dataframe["text"]
    # dropping any duplicates
    tweet_dataframe = tweet_dataframe.drop_duplicates()
    # cleaning tweets (if chosen)
    if clean_tweets == True:
        tweet_dataframe = tweet_dataframe.apply(clean_text)

    tweet_dataframe['sentiment'] = tweet_dataframe.apply(
        lambda text: TextBlob(text).sentiment)

    sentiment_list = tweet_dataframe['sentiment'].tolist()
    sentiment_columns = ['polarity', 'subjectivity']

    sentiment_only_df = pd.DataFrame(sentiment_list, columns=sentiment_columns)
    return sentiment_only_df


def mean_polarity_subjectivity(sentiment_df, drop_zero_values=False):
    polarities = sentiment_df['polarity'].tolist()
    subjectivities = sentiment_df['subjectivity'].tolist()

    if drop_zero_values == True:
        polarities = list(filter(lambda x: x != 0, polarities))
        subjectivities = list(filter(lambda x: x != 0, subjectivities))

    mean_polarity = sum(polarities)/len(polarities)
    mean_subjectivity = sum(subjectivities)/len(subjectivities)

    return mean_polarity, mean_subjectivity


def new_df_all_days_sentiment(all_days_folder_path, drop_zero_values=False, clean_tweets=True):
    output_df = pd.DataFrame()
    daily_tweet_folders = os.listdir(all_days_folder_path)
    daily_tweet_folders.sort(reverse=False)
    day_count = 0
    for folder in daily_tweet_folders:
        day_folder_path = os.path.join(all_days_folder_path, folder)
        file_names = os.listdir(day_folder_path)
        file_names.sort()
        file_count = 0
        day_df = pd.DataFrame()
        for file in file_names:
            print(f"processing {file}")
            coin, file_date = get_hashtag_and_date_from_csv_title(file)
            file_path = os.path.join(day_folder_path, file)
            file_df = dataframe_from_tweet_csv(file_path)
            file_df = sentiment_df_from_tweet_df(file_df)

            if drop_zero_values == True:
                file_polarity, file_subjectivity = mean_polarity_subjectivity(
                    file_df, drop_zero_values=True)
            else:
                file_polarity, file_subjectivity = mean_polarity_subjectivity(
                    file_df, drop_zero_values=False)

            if file_count == 0:
                day_sentiment_dict = {
                    'date': [file_date], f'{coin}_polarity': file_polarity, f'{coin}_subjectivity': file_subjectivity}
                day_df = pd.DataFrame(day_sentiment_dict)
            else:
                day_df[f'{coin}_polarity'] = file_polarity
                day_df[f'{coin}_subjectivity'] = file_subjectivity
            file_count += 1
        if day_count == 0:
            output_df = day_df
        else:
            output_df = pd.concat([output_df, day_df], ignore_index=True)
        day_count += 1
    return output_df

# -------------------------------------------------------------------------------
# Calls
# -------------------------------------------------------------------------------


this_folder = os.path.dirname(os.path.abspath(__file__))
csv_master_folder = os.path.join(
    os.path.dirname(this_folder), "tweet-csv-cleaned")


daily_sentiment_csv_no_zero = os.path.join(
    this_folder, "daily_sentiment_no_zero.csv")

daily_sentiment_df = new_df_all_days_sentiment(
    csv_master_folder, drop_zero_values=True)

daily_sentiment_df.to_csv(
    daily_sentiment_csv_no_zero, index=False, header=True, mode='w+')


daily_sentiment_csv = os.path.join(this_folder, "daily_sentiment.csv")

daily_sentiment_df = new_df_all_days_sentiment(
    csv_master_folder, drop_zero_values=False)

daily_sentiment_df.to_csv(
    daily_sentiment_csv, index=False, header=True, mode='w+')


# -------------------------------------------------------------------------------
# testing
# -------------------------------------------------------------------------------# trouble_df = new_df_single_day_hourly_tweetcount(trouble_day_folder)


# test_day_folder = os.path.join(csv_master_folder, "2021-03-01")
# test_file = os.path.join(test_day_folder, "2021-03-01-bitcoin-tweets.csv")

# df = dataframe_from_tweet_csv(test_file, "created_at")
# df_sentiment = sentiment_df_from_tweet_df(df)

# print(df_sentiment)

# polarities = df_sentiment['polarity'].tolist()
# print(sum(polarities)/len(polarities))
