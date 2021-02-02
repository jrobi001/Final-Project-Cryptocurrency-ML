import os
import shutil

this_folder = os.path.dirname(os.path.abspath(__file__))
snscrape_temp_folder = os.path.join(this_folder, "snscrape-temp")
print(snscrape_temp_folder)

snscrape_archive_folder = os.path.join(this_folder, "snscrape-archive")


def archive_old_snscrape_files(snscrape_temp_dir, hashtags, destination_dir):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    for hashtag in hashtags:
        hashtag_temp_dir = os.path.join(snscrape_temp_dir, hashtag)
        file_names = os.listdir(hashtag_temp_dir)
        for file in file_names:
            shutil.move(os.path.join(hashtag_temp_dir, file), destination_dir)
    return


hashtags = ["bitcoin", "ethereum"]
archive_old_snscrape_files(snscrape_temp_folder, hashtags,
                           snscrape_archive_folder)
