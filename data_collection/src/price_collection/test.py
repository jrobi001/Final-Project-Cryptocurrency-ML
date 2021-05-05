import os
import pandas as pd
from datetime import datetime, timedelta, date

# if try to run twice these will be the dates... I guess it would crash in this case?
start_date = str(date.today())
end_date = str(date.today() - timedelta(1))

start_date = "2021-04-28"
end_date = "2021-04-27"

print(start_date, end_date)

if datetime.strptime(start_date, '%Y-%m-%d') > datetime.strptime(end_date, '%Y-%m-%d'):
    print("oh no")
    print("it seems you have already run this file today")
    print("to override change the date in price_collection/start-date.txt")


end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(1)
print(str(end_date.date()))
