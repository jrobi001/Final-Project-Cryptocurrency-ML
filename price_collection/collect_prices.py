
import os
import pandas as pd
from datetime import datetime, timedelta, date
import san

this_folder = os.path.dirname(os.path.abspath(__file__))
output_folder = os.path.join(
    os.path.dirname(this_folder), "price-data")

auth_file = os.path.join(this_folder, 'auth.txt')
start_date_file = os.path.join(this_folder, 'start-date.txt')

cryptocurrencies = ["bitcoin", "ethereum", "dogecoin"]

first_run = False

# Setting up santiment api key (is single string stored in auth.txt)
auth_string = ''    # can remove below and provide key here directly
with open(auth_file) as f:
    for line in f:
        auth_string = line


# dates are inclusive, to run a single date, provide same value
start_date = "2021-01-31"
# collecting prices only up to midnight last night (as is same period tweets currently collected to)
end_date = str(date.today() - timedelta(1))


if not os.path.exists(start_date_file):
    first_run = True
else:
    with open(start_date_file) as f:
        for line in f:
            start_date = line


write_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(1)
write_date = str(write_date.date())
f = open(start_date_file, "w")
f.write(write_date)
f.close()

if datetime.strptime(start_date, '%Y-%m-%d') > datetime.strptime(end_date, '%Y-%m-%d'):
    print("oh no")
    print(f"it seems you have already collected prices up to {end_date}")
    print("to override change the date in price_collection/start-date.txt")

else:
    print(f"collecting prices between {start_date} and {end_date}")

    for coin in cryptocurrencies:
        query = "ohlcv/" + coin
        print(f"fetching hourly price data for {coin}")
        ohlcv_hourly_df = san.get(
            query,
            from_date=start_date,
            to_date=end_date,
            interval="1h"
        )

        if first_run:
            csv_path = os.path.join(output_folder, f"hourly-prices-{coin}.csv")
            ohlcv_hourly_df.to_csv(csv_path, index=True,
                                   header=True, mode='w+')
        else:
            csv_path = os.path.join(output_folder, f"hourly-prices-{coin}.csv")
            ohlcv_hourly_df.to_csv(csv_path, index=True,
                                   header=False, mode='a')

    for coin in cryptocurrencies:
        query = "ohlcv/" + coin
        print(f"fetching daily price data for {coin}")
        ohlcv_daily_df = san.get(
            query,
            from_date=start_date,
            to_date=end_date,
            interval="1d"
        )
        if first_run:
            csv_path = os.path.join(output_folder, f"daily-prices-{coin}.csv")
            ohlcv_daily_df.to_csv(csv_path, index=True, header=True, mode='w+')
        else:
            csv_path = os.path.join(output_folder, f"daily-prices-{coin}.csv")
            ohlcv_daily_df.to_csv(csv_path, index=True, header=False, mode='a')
