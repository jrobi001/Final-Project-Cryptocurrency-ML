import os
import shutil
import tweepy
from datetime import date, timedelta


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


bad_tweet_ids = [362388279052689411, 362476987542097922,
                 1358203372931842052, 1358232653028327425, 1356263332307582978]

chunk_bad_tweets = api.statuses_lookup(bad_tweet_ids, tweet_mode="extended")

for tweet in chunk_bad_tweets:
    tweet = create_tweet_csv_entry_from_api_status(tweet)
    print(repr(tweet))

# current_folder = os.path.dirname(os.path.abspath(__file__))
# print(current_folder)

# -------------------------------------------------------------------------------

# today = date.today()
# yesterday = today - timedelta(1)

# this_folder = os.path.dirname(os.path.abspath(__file__))
# csv_path = os.path.join(this_folder, "csv-tweet-files", str(yesterday), "")
# print(csv_path)

# today = date.today() - timedelta(1)
# yesterday = today - timedelta(1)
# print(today, yesterday)

# this_folder = os.path.dirname(os.path.abspath(__file__))
# snscrape_temp_folder = os.path.join(this_folder, "snscrape-temp", "bitcoin")
# print(snscrape_temp_folder)
# files = os.listdir(snscrape_temp_folder)
# print(files)
# print(type(files))
# if files == []:
#     print("yes")
# if len(files) == 0:
#     print("no")

# hashtags = ["yes"]

# for hashtag in hashtags:
#     print("works")


# snscrape_archive_folder = os.path.join(this_folder, "snscrape-archive")


# def archive_old_snscrape_files(snscrape_temp_dir, hashtags, destination_dir):
#     if not os.path.exists(destination_dir):
#         os.makedirs(destination_dir)
#     for hashtag in hashtags:
#         hashtag_temp_dir = os.path.join(snscrape_temp_dir, hashtag)
#         file_names = os.listdir(hashtag_temp_dir)
#         for file in file_names:
#             shutil.move(os.path.join(hashtag_temp_dir, file), destination_dir)
#     return


# hashtags = ["bitcoin", "ethereum"]
# archive_old_snscrape_files(snscrape_temp_folder, hashtags,
#                            snscrape_archive_folder)
