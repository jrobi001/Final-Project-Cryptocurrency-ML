import os
import glob
from datetime import timedelta
import shutil

# TODO: modify to take lists of related hashtags and put into directories of the first hashtag in each list


def snscrape_tweets_hashtags(hashtags, since, until, folder):
    """Issues terminal commands to collect tweets using snscrape between the 
    dates provided, into txt files in the directory provided.
    Sub-folders are created for each hashtag in the directory provided.

    Args:
        hashtags (list[string]): Array/list of hashtags (without the # symbol before)
        since ([date]): inclusive fomat: YYYY-MM-DD
        until ([date]): exclusive fomat: YYYY-MM-DD
        folder (path[string]): path to folder to save, including final folder '/'
    """
    day_before_until = until - timedelta(1)
    for hashtag in hashtags:
        hashtag_folder = os.path.join(folder, hashtag, "")
        if not os.path.exists(hashtag_folder):
            os.makedirs(hashtag_folder)
        command = f"snscrape twitter-search '#{hashtag} since:{since} until:{until}' >{hashtag_folder}sns-{hashtag}-{since}-to-{day_before_until}.txt"
        print(command)
        os.system(command)


# Separate out the id's
# Already set up to take multiple files and remove duplicates, modify to only require folder
def snscrape_separate_ids(hashtag, folder):
    """Separates out the tweet id's from snscrape files. If multiple snscrape
    files, merges them into a single tweet id list. i.e. multiple related
    hashtag snscrape files stored in the same folder e.g. #Bitcoin and #BTC

    Args:
        hashtag (string): Name of primary hashtag merging on (only used for console message)
        folder (string): Folder path of snscrape files to merge (should not include trailing '/' at end)

    Returns:
        list: List of unique tweet ids (from all snscrape files in folder provided)
    """
    # adding trailing '/' to folder path
    path = os.path.join(folder, "")
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
    # ensuring no duplicate keys
    id_keys = list(dict.fromkeys(id_keys))
    final_count = len(id_keys)
    print(f"\n{final_count} unique #{hashtag} tweet ids seperated with {count - final_count} duplicates removed\n")
    return id_keys


def move_snscrape_files(snscrape_temp_dir, hashtags, destination_dir):
    """Moves snscrape files from the temporary directory, to an archive folder.
    Snscrape files in the temp directory used for tweet collection, move them to
    allow new snscrape files to take their place.

    Args:
        snscrape_temp_dir (string): folder path of temporary snscrape files
        hashtags (list of str): list of hashtags (used to collect tweets and name temp snscrape folder paths)
        destination_dir (string): folder path of archived snscrape files
    """
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    for hashtag in hashtags:
        hashtag_temp_dir = os.path.join(snscrape_temp_dir, hashtag)
        file_names = os.listdir(hashtag_temp_dir)
        if len(file_names) == 0:
            continue
        for file in file_names:
            shutil.move(os.path.join(hashtag_temp_dir, file), destination_dir)
    return
