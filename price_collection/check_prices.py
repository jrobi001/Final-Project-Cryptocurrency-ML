import os
import pandas as pd
from datetime import datetime, timedelta, date

this_folder = os.path.dirname(os.path.abspath(__file__))
output_folder = os.path.join(
    os.path.dirname(this_folder), "price-data")

output_filenames = os.listdir(output_folder)
hourly_filenames = [
    output_filenames for output_filenames in output_filenames if output_filenames.startswith("hourly")]

for file in hourly_filenames:
    path = os.path.join(output_folder, file)
    df = pd.DataFrame()
    for chunk in pd.read_csv(path, chunksize=4000):
        df = df.append(chunk)
    df["datetime"] = pd.to_datetime(df["datetime"], errors='coerce')
    daily_frames = df.groupby(pd.Grouper(key="datetime", freq="D"))
    for group, frame in daily_frames:
        if len(frame) != 24:
            print(path)
            # print(group)
            print(len(frame))
            # hourly_frames = frame.groupby(pd.Grouper(key="datetime", freq="H"))
            # for group, frame in hourly_frames:
            #     print(group)
