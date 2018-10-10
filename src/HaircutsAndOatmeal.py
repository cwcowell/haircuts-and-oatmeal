import Helpers
import Models
import numpy as np
import os
import sqlite3
import typing

# how much to spend when buying a stock
BUY_BUDGET: float = 1000.0

# how high a stock can rise before we sell it to take profits
RISE_LIMITS: typing.List = np.logspace(0, 2, 10)

# how far a stock can sink before we sell it, to protect against further losses
SINK_LIMITS: typing.List = np.logspace(0, 2, 10)

# how long to wait after selling a stock, before automatically buying that stock again
COOL_OFF_SPANS: typing.List = np.round(np.logspace(0, 2, 10))

# how many days' worth of price history a stock needs to be considered valid
REQUIRED_NUM_HISTORICAL_PRICES = 1259

# file paths
THIS_FILE_PATH: str = os.path.split(os.path.abspath(__file__))[0]
REPO_ROOT: str = os.path.join(THIS_FILE_PATH, '..')
DB_FILE_PATH: str = os.path.join(REPO_ROOT, 'data', 'SandP500.sqlite3')
RESULTS_FILE_PATH: str = os.path.join(REPO_ROOT, 'data', 'results.csv')


# ----- MAIN LOGIC -----

conn = sqlite3.connect(DB_FILE_PATH)
tickers = Helpers.get_all_tickers(conn)
initial_cash_balance = BUY_BUDGET * len(tickers)
portfolio = Models.Portfolio()
for ticker in tickers:
    portfolio.add_ticker(ticker, REQUIRED_NUM_HISTORICAL_PRICES, conn)
conn.close()

Helpers.prep_results_file(RESULTS_FILE_PATH)

for rise_limit in RISE_LIMITS:
    for sink_limit in SINK_LIMITS:
        for cool_off_span in COOL_OFF_SPANS:
            print("-----")
            portfolio.run_simulation(initial_cash_balance, BUY_BUDGET, rise_limit, sink_limit, cool_off_span)
            portfolio.report_results(RESULTS_FILE_PATH)

# Buy and hold for five years
print("-----")
portfolio.run_simulation(initial_cash_balance, BUY_BUDGET, -1, -1, 0)
portfolio.report_results(RESULTS_FILE_PATH)
