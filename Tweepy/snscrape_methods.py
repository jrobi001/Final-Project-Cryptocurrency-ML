import os
import glob
from datetime import timedelta


def snscrape_tweets_hashtags(hashtags, since, until, folder):
    # Might want to collect them in the same folder, to seperate out duplicates between the two collections?
    """Issues terminal commands to collect tweets using snscrape between the dates provided, into txt files in the directory provided.
    Sub-folders are created for each hashtag in the directory provided.

    Args:
        hashtags (list[string]): Array/list of hashtags (without the # symbol before)
        since ([date]): inclusive fomat: YYYY-MM-DD
        until ([date]): exclusive fomat: YYYY-MM-DD
        folder (path[string]): path to folder to save, including final folder '/'
    """
    day_before_until = until - timedelta(1)
    for hashtag in hashtags:
        if not os.path.exists(f"{folder}{hashtag}"):
            os.makedirs(f"{folder}{hashtag}")
        command = f"snscrape twitter-search '#{hashtag} since:{since} until:{until}' >{folder}{hashtag}/sns-{hashtag}-{since}-to-{day_before_until}.txt"
        print(command)
        os.system(command)


# Separate out the id's

def snscrape_separate_ids(hashtag, folder):
    # Might want to filter out duplicates shared between hashtags in future
    # or have them as a seperate list?
    path = folder + hashtag + "/"
    id_keys = []
    count = 0
    if not os.path.exists(path):
        print("Error: Path does not exist: " + path)
        return  # TODO: catch exception
    files = glob.glob(path+"*.txt")
    if files == []:
        print("There are no files in" + path)
        return  # TODO: catch exception
    for file in files:
        with open(file, "rb") as current_file:
            for line in current_file.read().splitlines():
                tweet_id = str(line).split("/")[-1].split("'")[0]
                id_keys.append(tweet_id)
                count += 1
        # TODO: move files to storage folder after processed?
    # ensuring no duplicate keys
    id_keys = list(dict.fromkeys(id_keys))
    final_count = len(id_keys)
    print(f"{final_count} unique #{hashtag} tweet ids seperated with {final_count - count} duplicates removed")
    return id_keys
