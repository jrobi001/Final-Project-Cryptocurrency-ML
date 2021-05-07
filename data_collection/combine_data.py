import os
import pandas as pd
from datetime import timedelta

# TODO:
# - Rename all time columns to 'datetime' and merge on that
# - Check the second datetime column is dropped when do
# - combine into function args (coin, tweet_file, price_file)
# - decide if separate similar function for daily datasets (or combine)
# - maybe offer options in the case of incomplete data, instead of longes sequence
# - the process is fast enough, but could set it to append new data, rather than re-making the file each day
#   on the other hand, reminding collector of the missing data each day might actually be preferable

this_folder = os.path.dirname(os.path.abspath(__file__))

tweet_file = os.path.join(this_folder, "dogecoin_hourly.csv")
price_file = os.path.join(this_folder, "hourly-prices-dogecoin.csv")
# open both files as pandas dataframes

tweet_df = pd.read_csv(tweet_file)
price_df = pd.read_csv(price_file)

output_df = pd.DataFrame()

missing_data = False

# find and print out any missing data from each file individually
tweet_df["time"] = pd.to_datetime(tweet_df["time"], errors='coerce', utc=True)
price_df["datetime"] = pd.to_datetime(
    price_df["datetime"], errors='coerce', utc=True)

if len(tweet_df) != len(price_df):
    missing_data = True


frames_tweet_df = tweet_df.groupby(pd.Grouper(key="time", freq="D"))
frames_price_df = price_df.groupby(pd.Grouper(key="datetime", freq="D"))


for group, frame in frames_tweet_df:
    if len(frame) != 24:
        print("Missing tweet data: {0} hours missing from {1}".format(
            24 - len(frame), group.date()))

for group, frame in frames_price_df:
    if len(frame) != 24:
        print("Missing price data: {0} hours missing from {1}".format(
            24 - len(frame), group.date()))


# perform inner join on datetime (so that only complete data kept)
combined_df = pd.merge(tweet_df, price_df, how='inner',
                       left_on="time", right_on="datetime")

# combined_df.to_csv(os.path.join(this_folder, "test.csv"))

# determine the longest sequence(s) of complete data
# ask whether to proceed?
complete_sequences = []
sequence = [None, None]
combined_df = combined_df.groupby(pd.Grouper(key="datetime", freq="D"))
first_date = True
for group, frame in combined_df:
    if first_date and len(frame) == 24:
        sequence[0] = group.date()
        first_date = False
    elif first_date and len(frame) != 24:
        continue
    elif len(frame) != 24:
        sequence[1] = group.date()
        complete_sequences.append(sequence.copy())
        sequence[0] = group.date() + timedelta(1)
    else:
        sequence[1] = group.date()

complete_sequences.append(sequence.copy())

longest_sequence = []
len_longest = timedelta(0)

for sequence in complete_sequences:
    dif = sequence[1] - sequence[0]
    if dif > len_longest:
        len_longest = dif
        longest_sequence = sequence

print("The longest complete sequence of data found was between {0} and {1}".format(
    str(longest_sequence[0]), str(longest_sequence[1])
))
print("This timeperiod will be used to create the dataset\n")
print("To use the full time-period, please resolve the missing data\n")
print("Or, to remove this message set the collection start period to after the data discrepancy\n")

start_date = longest_sequence[0]
end_date = longest_sequence[1]

# filter the inner join to the longest date range
for group, frame in combined_df:
    if group < start_date or group > end_date:
        continue
    else:
        output_df = output_df.append(frame)


output_df.to_csv(os.path.join(this_folder, "test.csv"),
                 index=False, header=True, mode="w+")

print("The combined dataset from the time period {0} to {1} has been saved".format(
    str(longest_sequence[0]), str(longest_sequence[1])
))
# Eventually also need method to carry on from last date in combined file
# and handle issue if new data is incomplete

# actually add different method to append to existing dataset, with a throw error if most recently collected data is mismatched?
