import pandas as pd
import time
import os
from datetime import date, datetime, timedelta

current_folder = os.path.dirname(os.path.abspath(__file__))
test_csv = os.path.join(current_folder, 'input-csv',
                        '2021-02-11-ethereum-tweets.csv')

example_time = "2021-02-11 23:01:43"
date, time = example_time.split(' ')
date_time = datetime.fromisoformat(example_time)
date, time = date_time.date(), date_time.time()
file_date = datetime.fromisoformat("2021-02-11").date()
print(file_date)


df = pd.read_csv(
    test_csv)  # , dtype='string', chunksize=4000, low_memory=False)

# print(df.iloc[0])

df['created_at'] = pd.to_datetime(df['created_at'])
df = df.set_index(df['created_at'])
df = df.sort_index()

# -------------------------------------------------------------------------------
# method of grouping tweets by hour
# https://realpython.com/pandas-groupby/#how-pandas-groupby-works
df_hourly = df.groupby(pd.Grouper(key="created_at", freq='H'))

# methods of iterating over grouped tweets by hour
for group, frame in df_hourly:
    print(group)
    print(len(frame))

hour, frame = next(iter(df_hourly))
print(hour)
print(frame.head(3))
# -------------------------------------------------------------------------------

# one method of making sure all entries have the right date.
# for index, row in df.iterrows():
#     print(row[3])
#     date_time = datetime.fromisoformat(row[3])
#     print(date_time)
#     date, time = date_time.date(), date_time.time()
#     if date != file_date:
#         print(date)
