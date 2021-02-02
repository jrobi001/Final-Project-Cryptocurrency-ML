import os
import pandas as pd
from tqdm import tqdm


def extract_hastags_from_entities(entities_hashtag):
    hashtags_string = ""
    for i in range(len(entities_hashtag)):
        hashtags_string = hashtags_string + "#" + entities_hashtag[i]['text']
    return hashtags_string


def create_tweet_csv_entry_from_api_status(status):
    hashtags = extract_hastags_from_entities(status.entities['hashtags'])
    tweet = {
        "id_str": str(status.id_str),
        "from_user": status.user.name,              # TODO: wrong name field
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
        "hashtags": hashtags
    }
    return tweet


def chunkify_tweet_ids(tweet_id_list, chunk_size):
    for i in range(0, len(tweet_id_list), chunk_size):
        yield tweet_id_list[i:i + chunk_size]


def get_tweets_and_create_csv(tweepy_api, tweet_id_list, chunk_size, folder_path, name):
    csv_path = os.path.join(folder_path, "csv-tweet-files", "")
    if not os.path.exists(csv_path):
        os.makedirs(csv_path)
    filename = csv_path + name + ".csv"
    print("writing to: " + name + ".csv")
    chunked_tweet_ids = list(chunkify_tweet_ids(tweet_id_list, chunk_size))

    number_of_chunks = len(chunked_tweet_ids)
    progress_bar = tqdm(total=number_of_chunks)

    include_header = True
    for chunk in chunked_tweet_ids:

        chunk_statuses = tweepy_api.statuses_lookup(
            chunk, tweet_mode="extended")

        last_tweet = create_tweet_csv_entry_from_api_status(
            chunk_statuses.pop())

        csv_dataframe = pd.DataFrame(
            last_tweet, columns=last_tweet.keys(), index=[0])

        for status in chunk_statuses:
            tweet = create_tweet_csv_entry_from_api_status(status)
            csv_dataframe = csv_dataframe.append(tweet, ignore_index=True)

        csv_dataframe.to_csv(filename, index=False,
                             header=include_header, mode='a')
        include_header = False
        progress_bar.update(1)
    progress_bar.close()
    return
