import Helpers
import Models
import os
import sqlite3
import typing

# how much to spend when buying a stock
BUY_BUDGET: float = 1000.0

# how high a stock can rise before we sell it to take profits
RISE_LIMITS: typing.List = [.1, .25, .75, .96]

# how far a stock can sink before we sell it, to protect against further losses
# SINK_LIMITS: typing.List = [0.02, .1, .15, .25]
SINK_LIMITS: typing.List = [.3]

# how long to wait after selling a stock, before automatically buying that stock again
# COOL_OFF_SPANS: typing.List = [3, 10, 30]
COOL_OFF_SPANS: typing.List = [10]

THIS_FILE_PATH: str = os.path.split(os.path.abspath(__file__))[0]
REPO_ROOT: str = os.path.join(THIS_FILE_PATH, '..')
DB_FILE_PATH: str = os.path.join(REPO_ROOT, 'data', 'SandP500.sqlite3')


# ----- MAIN LOGIC -----

conn = sqlite3.connect(DB_FILE_PATH)
tickers = Helpers.get_all_tickers(conn)
initial_cash_balance = BUY_BUDGET * len(tickers)
if Helpers.is_limit_tickers_on():
    tickers = tickers[:5]
portfolio = Models.Portfolio()
for ticker in tickers:
    portfolio.add_ticker(ticker, conn)
conn.close()

for rise_limit in RISE_LIMITS:
    for sink_limit in SINK_LIMITS:
        for cool_off_span in COOL_OFF_SPANS:
            print("-----")
            portfolio.run_simulation(initial_cash_balance, BUY_BUDGET, rise_limit, sink_limit, cool_off_span)
            portfolio.print_parms()
            portfolio.print_final_stats()

# Buy and hold for five years
print("-----")
portfolio.run_simulation(initial_cash_balance, BUY_BUDGET, -1, -1, 0)
portfolio.print_parms()
portfolio.print_final_stats()
