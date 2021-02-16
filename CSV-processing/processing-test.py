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

# for i in range(0, 24):

df_hourly = df.groupby(pd.Grouper(key="created_at", freq='H'))

for group in df_hourly:
    print(group[0])


# for index, row in df.iterrows():
#     print(row[3])
# date_time = datetime.fromisoformat(row[3])
# print(date_time)
# date, time = date_time.date(), date_time.time()
# if date != file_date:
#     print(date)
# if time.hour == 1:
#     print(time)
