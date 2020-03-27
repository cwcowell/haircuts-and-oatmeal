import os
import sqlite3
import typing

import numpy as np

import Helpers
import Models

# how much to spend when buying a stock
BUY_BUDGET: int = 1000

# how high a stock can rise before we sell it to take profits
# RISE_LIMITS: typing.List[int] = np.logspace(0.1, 2, 10, dtype=int)
RISE_LIMITS: np.ndarray = np.logspace(0.1, 2, 10, dtype=int)

# how far a stock can sink before we sell it, to protect against further losses
SINK_LIMITS: np.ndarray = np.logspace(0.1, 2, 10, dtype=int)

# how long to wait after selling a stock, before automatically buying that stock again
COOL_OFF_SPANS: np.ndarray = np.logspace(0.1, 2, 10, dtype=int)

# how many days of historical prices a stock needs to be considered valid
REQUIRED_NUM_HISTORICAL_PRICES: int = 1259

# file paths
THIS_FILE_PATH: str = os.path.split(os.path.abspath(__file__))[0]
REPO_ROOT: str = os.path.join(THIS_FILE_PATH, '..')
DB_FILE_PATH: str = os.path.join(REPO_ROOT, 'data', 'SandP500.sqlite3')
RESULTS_FILE_PATH: str = os.path.join(REPO_ROOT, 'data', 'results.csv')


def make_portfolio() -> Models.Portfolio:
    with sqlite3.connect(DB_FILE_PATH) as conn:
        tickers: typing.List[str] = Helpers.get_all_tickers(conn)
        portfolio = Models.Portfolio(BUY_BUDGET)
        for ticker in tickers:
            portfolio.add_ticker(ticker, REQUIRED_NUM_HISTORICAL_PRICES, conn)
    return portfolio


def run_simulation(portfolio: Models.Portfolio) -> None:
    Helpers.prep_results_file(RESULTS_FILE_PATH)
    for rise_limit in RISE_LIMITS:
        for sink_limit in SINK_LIMITS:
            for cool_off_span in COOL_OFF_SPANS:
                print("-----")
                portfolio.process_all_days(rise_limit, sink_limit, cool_off_span)
                portfolio.report_results(RESULTS_FILE_PATH, rise_limit, sink_limit, cool_off_span)
                portfolio.reset()

    # buy and hold for five years, for comparison
    print("-----")
    rise_limit = -1
    sink_limit = -1
    cool_off_span = 0
    portfolio.process_all_days(rise_limit, sink_limit, cool_off_span)
    portfolio.report_results(RESULTS_FILE_PATH, rise_limit, sink_limit, cool_off_span)


def main() -> None:
    portfolio = make_portfolio()
    run_simulation(portfolio)


if __name__ == "__main__":
    main()
