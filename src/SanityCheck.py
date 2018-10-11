import sqlite3

import numpy as np

import Helpers

conn = sqlite3.connect('../data/SandP500.sqlite3')
all_tickers = Helpers.get_all_tickers(conn)

cursor = conn.cursor()
prices_at_start = np.array([])
prices_at_end = np.array([])

for ticker in all_tickers:
    cursor.execute("SELECT closing_price "
                   "FROM historical_prices "
                   f"WHERE ticker is '{ticker}'"
                   "AND date is '2013-02-08'")
    all_rows = cursor.fetchall()
    if len(all_rows) == 0:
        continue
    print(ticker)
    price_at_start = all_rows[0]
    prices_at_start = np.append(prices_at_start, price_at_start)


for ticker in all_tickers:
    cursor.execute("SELECT closing_price "
                   "FROM historical_prices "
                   f"WHERE ticker is '{ticker}'"
                   "AND date is '2018-02-07'")
    all_rows = cursor.fetchall()
    if len(all_rows) == 0:
        continue
    print(ticker)
    price_at_end = all_rows[0]
    prices_at_end = np.append(prices_at_end, price_at_end)


sum_of_prices_at_start = prices_at_start.sum()
sum_of_prices_at_end = prices_at_end.sum()
difference_of_sums = sum_of_prices_at_end - sum_of_prices_at_start
percent_change = difference_of_sums / sum_of_prices_at_start

print(sum_of_prices_at_start)
print(sum_of_prices_at_end)
print(difference_of_sums)
print(percent_change)
