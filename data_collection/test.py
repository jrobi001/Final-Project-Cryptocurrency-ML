import os

this_folder = os.path.dirname(os.path.abspath(__file__))

folder_data = os.path.join(this_folder, "data")

folder_processed_tweets = os.path.join(folder_data, "processed-tweet-data")

processed_filenames = os.listdir(folder_processed_tweets)

processed_filenames = [
    processed_filenames for processed_filenames in processed_filenames if processed_filenames.endswith(".csv")]

f_path = "/home/jabba/Desktop/Final-Project-Cryptocurrency-ML/data_collection/data/price_data/hourly-prices-bitcoin.csv"

f_path = os.path.dirname(f_path)

if os.path.exists(f_path):
    print('yes')
else:
    print('no')
    print(f_path)
