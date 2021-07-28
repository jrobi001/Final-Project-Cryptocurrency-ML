# %%
import os
import pandas as pd
from datetime import datetime, timedelta, date
import san

this_folder = os.path.dirname(os.path.abspath(__file__))

auth_file = os.path.join(this_folder, 'auth.txt')

auth_string = ''
with open(auth_file) as f:
    for line in f:
        auth_string = line


start = "2021-06-10"
end = "2021-06-11"

query = "ohlc/bitcoin"
ohlcv_hourly_df = san.get(
    query,
    from_date=start,
    to_date=end,
    interval="1h"
)

# %%
print(len(ohlcv_hourly_df))
# %%
