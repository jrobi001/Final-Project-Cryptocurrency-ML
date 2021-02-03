# 0-Notes: First Model Attempt

Aims:

- Process time series bitcoin data into tensors, usable by ML model
- Use hourly data, sourced from Binance exchange
- Create and run a proof of concept simple LSTM model

Data:

- From: 2017-08-17 04-AM 
- To: 2021-02-03 00:00:00
- 33,022 rows in CSV
- May be some duplicate entries - 1266 days = 30,384 hrs (2k+ less)
- Columns: unix, date, symbol, open, high, low, close, Volume BTC, Volume USDT, tradecount

| Column      | Example             |
| ----------- | ------------------- |
| unix        | 1612310400000       |
| date        | 2021-02-03 00:00:00 |
| symbol      | BTC/USDT            |
| open        | 35472.71            |
| high        | 35618.75            |
| low         | 35362.38            |
| close       | 35476.99            |
| Volume BTC  | 518.474918          |
| Volume USDT | 18393856.0883226    |
| tradecount  | 10423               |

- There is an increase in precision of data and inclusion of `tradecount` from `2020-08-01 23:00:00` on-wards.![](img/0-1-change-precision-and-date.png)*
- There is also a duplication of data between `2020-08-01 23:00:00` and `2020-11-20 07:00:00`, with there being entries for each hour in both the lower precision previous format and the higher precision new format
  - row 1790 to 7087![](img/0-2-end-duplication.png)

I can either filter out these duplications somehow, or use the consistent data between `2017-08-17 04-AM ` and `2020-08-01 11-PM`

I will need to filter out and remove these duplications in the future, but for today I want to ensure I get through basic processing and target creation along with training a first model. If I have time I will return to creating a pandas script to delete these duplications later today, but for now I will just use the data up to `2020-08-01 11-PM`.

The change in precision of columns: `open, high, low, close, Volume BTC, Volume USDT` should not matter too much for `open, high, low, close` the precision only added 0s, no extra precision.  `Volume BTC, Volume USDT` did increase in precision by 4dp and 6dp respectively (both from 2dp). I am not certain, but I do not believe this should affect things much. As a precaution the new data could be reduced to 2dp before vectorisation to keep consistency.

