import os
import sqlite3
import typing

import pandas as pd
from termcolor import cprint

import Helpers


class Stock:
    def __init__(self, ticker: str, price_history: pd.DataFrame) -> None:
        self.ticker: str = ticker
        self.price_history: pd.DataFrame = price_history
        self.last_sell_date_idx: int = 0
        self.shares: float = 0.0
        self.last_bought_at_price: float = 0.0

    def are_historical_prices_complete(self, required_num_historical_prices: int) -> bool:
        """Determine if the price history is complete--we can't use stocks with partial histories."""
        if required_num_historical_prices == -1:
            # -1 signals that we're in test mode, so price history is always valid
            return True
        else:
            return len(self.price_history) == required_num_historical_prices

    def buy(self, date_idx: int, cash_balance: float, buy_budget: float) -> float:
        """Buy a fixed value worth of shares of this stock, and return post-purchase cash balance."""
        todays_price: float = float(self.price_history.iat[date_idx, 1])
        bought_shares: float = buy_budget / todays_price
        self.shares: float = bought_shares
        new_cash_balance: float = cash_balance - buy_budget
        self.last_bought_at_price: float = todays_price
        if Helpers.is_verbose_on():
            print(f"{self.ticker}: buy {self.shares:.2f} shares at {todays_price:.2f} "
                  f"for ${buy_budget:.2f} on date {date_idx}. Cash balance: {new_cash_balance:.2f}")
        return new_cash_balance

    def sell(self, date_idx: int, cash_balance: float, buy_budget: float) -> float:
        """Sell all shares of this stock and return post-sale cash balance."""
        todays_price: float = self.price_history.iat[date_idx, 1]
        sell_value: float = self.shares * todays_price
        new_cash_balance: float = cash_balance + sell_value
        profit_or_loss = sell_value - buy_budget
        if Helpers.is_verbose_on():
            if profit_or_loss >= 0:
                text_color: str = 'green'
            else:
                text_color = 'red'
            cprint(f"{self.ticker}: sell {self.shares:.2f} shares at {todays_price:.2f} "
                   f"for ${sell_value:.2f} on date {date_idx}. Cash balance: {new_cash_balance:.2f}",
                   text_color)
        self.shares = 0
        self.last_sell_date_idx = date_idx
        return new_cash_balance

    def is_below_sink_limit(self, date_idx: int, sink_limit_percent: float) -> bool:
        if sink_limit_percent == -1:
            return False
        else:
            sink_limit_price = self.last_bought_at_price - (self.last_bought_at_price * (sink_limit_percent / 100))
            below: bool = self.price_history.iat[date_idx, 1] <= sink_limit_price
            return below

    def is_above_rise_limit(self, date_idx: int, rise_limit_percent: float) -> bool:
        if rise_limit_percent == -1:
            return False
        else:
            rise_limit_price = self.last_bought_at_price + (self.last_bought_at_price * (rise_limit_percent / 100))
            is_above: bool = self.price_history.iat[date_idx, 1] >= rise_limit_price
            return is_above

    def are_any_shares_owned(self) -> bool:
        return self.shares > 0

    def are_no_shares_owned(self) -> bool:
        return not self.are_any_shares_owned()


class Portfolio:
    THIS_FILE_PATH: str = os.path.split(os.path.abspath(__file__))[0]
    REPO_ROOT: str = os.path.join(THIS_FILE_PATH, '..')
    PICKLE_DIR: str = os.path.join(REPO_ROOT, 'data', 'pickles')

    def __init__(self, buy_budget: float) -> None:
        self.stocks: typing.List[Stock] = []
        self.buy_budget: float = buy_budget

    def load_pickled_price_history(self, ticker: str) -> pd.DataFrame:
        """Read price data for this stock from a pickled file."""
        try:
            price_history = pd.read_pickle(f"../data/pickles/{ticker}.pkl")
            return price_history
        except FileNotFoundError:
            print(f"no pickle available for {ticker}; falling back to DB")
            return None

    def load_db_price_history(self, ticker: str, conn: sqlite3.Connection) -> pd.DataFrame:
        """Read price data for this stock from the DB, then pickle it for faster reference in the future."""
        sql = f"SELECT date, closing_price FROM historical_prices WHERE ticker = '{ticker}' ORDER BY date;"
        price_history = pd.read_sql(sql, conn)

        if not os.path.exists(Portfolio.PICKLE_DIR):
            os.mkdir(Portfolio.PICKLE_DIR)
        price_history.to_pickle(f"../data/pickles/{ticker}.pkl")
        return price_history

    def load_price_history(self, ticker: str, conn: sqlite3.Connection) -> pd.DataFrame:
        """Load price history from pickle (preferred, because fast) or DB (fallback, because slow)."""
        price_history = self.load_pickled_price_history(ticker)
        if price_history is None:
            price_history = self.load_db_price_history(ticker, conn)
        return price_history

    def add_ticker(self,
                   ticker: str,
                   required_num_historical_prices: int,
                   conn: sqlite3.Connection,
                   price_history: pd.DataFrame = None) -> None:
        if price_history is None:
            price_history = self.load_price_history(ticker, conn)

        # create a new Stock instance and add it to the portfolio
        stock = Stock(ticker, price_history)
        if stock.are_historical_prices_complete(required_num_historical_prices):
            self.stocks.append(stock)
            print(f"added {ticker} to portfolio")
        else:
            print(f"rejected {ticker} from portfolio because of incomplete price history")

    def ramp_up(self) -> None:
        """Buy initial shares of each stock."""
        self.cash_balance: float = self.initial_cash_balance()
        for stock in self.stocks:
            initial_date_idx = 0
            self.cash_balance = stock.buy(initial_date_idx, self.cash_balance, self.buy_budget)

    def ramp_down(self) -> None:
        """Sell all shares of all stocks at the end of the simulation."""
        for stock in self.stocks:
            if stock.are_any_shares_owned():
                self.cash_balance = stock.sell(-1, self.cash_balance, self.buy_budget)

    def process_one_day(self,
                        rise_limit: float,
                        sink_limit: float,
                        cool_off_span: int,
                        date_idx: int) -> None:
        for stock in self.stocks:
            take_gains: bool = stock.is_above_rise_limit(date_idx, rise_limit)
            limit_losses: bool = stock.is_below_sink_limit(date_idx, sink_limit)
            cool_off_expired: bool = date_idx - stock.last_sell_date_idx > cool_off_span

            if stock.are_any_shares_owned() and (take_gains or limit_losses):
                self.cash_balance = stock.sell(date_idx, self.cash_balance, self.buy_budget)
            elif stock.are_no_shares_owned() and cool_off_expired:
                self.cash_balance = stock.buy(date_idx, self.cash_balance, self.buy_budget)

    def process_all_days(self,
                         rise_limit: float,
                         sink_limit: float,
                         cool_off_span: int) -> None:
        """Run the time machine. This is where the magic happens."""
        self.ramp_up()
        for date_idx in range(1, len(self.stocks[0].price_history)):
            self.process_one_day(rise_limit, sink_limit, cool_off_span, date_idx)
        self.ramp_down()

    def initial_cash_balance(self) -> float:
        """Calculate how much cash the portfolio had before buying any stocks.
        This amount should be just enough to buy a fixed value worth of each of
        the S&P 500 stocks."""
        return self.buy_budget * len(self.stocks)

    def reset(self) -> None:
        """Reset the cash balance to whatever's needed to buy a fixed value of every stock."""
        self.cash_balance = self.initial_cash_balance()

    def report_results(self,
                       results_file_path: str,
                       rise_limit: float,
                       sink_limit: float,
                       cool_off_span: int) -> None:
        grand_profit = self.cash_balance - self.initial_cash_balance()
        grand_percent_change = grand_profit / self.initial_cash_balance() * 100

        print(f"rise_limit: {rise_limit}, sink_limit: {sink_limit}, cool off span: {cool_off_span}")
        print(f"grand profit: ${grand_profit:.0f}")
        print(f"grand percent change: {grand_percent_change:.0f}%")

        with open(results_file_path, 'a') as results_file:
            results_file.write(f'{rise_limit},{sink_limit},{cool_off_span},{grand_percent_change:.0f}\n')
