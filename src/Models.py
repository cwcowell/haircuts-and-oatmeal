import sqlite3
import typing

import pandas as pd
from termcolor import cprint

import Helpers


class Stock:
    def __init__(self, ticker: str, price_history: pd.DataFrame) -> None:
        self.ticker: str = ticker
        self.price_history: pd.DataFrame
        self.price_history = price_history
        self.shares: float
        self.last_bought_at_price: float
        self.last_sell_date_idx: int = 0

    def are_historical_prices_complete(self, required_num_historical_prices: int) -> bool:
        """Determine if the price history is complete--we can't use stocks with partial histories."""
        if required_num_historical_prices == -1:
            # -1 signals that we're in test mode, so price history is always valid
            return True
        else:
            return len(self.price_history) == required_num_historical_prices

    def buy(self, date_idx: int, cash_balance: float, buy_budget: float) -> float:
        """Buy a fixed dollars' worth of shares of this stock."""
        bought_shares: float = buy_budget / float(self.price_history.iat[date_idx, 1])
        new_cash_balance: float = cash_balance - buy_budget
        self.shares: float = bought_shares
        self.last_bought_at_price: float = self.price_history.iat[date_idx, 1]
        if Helpers.is_verbose_on():
            print("{}:  buy {:.2f} shares at {:.2f} for ${:.2f} on date {}. Cash balance: {:.2f}".format(
                self.ticker, self.shares, self.last_bought_at_price, buy_budget, date_idx, new_cash_balance))
        return new_cash_balance

    def sell(self, date_idx: int, cash_balance: float, original_purchase_value: float) -> float:
        """Sell all shares of this stock and reflect any profit/loss in the cash balance."""
        sell_value = self.shares * self.price_history.iat[date_idx, 1]
        new_cash_balance: float = cash_balance + sell_value
        profit_or_loss = sell_value - original_purchase_value
        if Helpers.is_verbose_on():
            if profit_or_loss >= 0:
                text_color = 'green'
            else:
                text_color = 'red'
            cprint("{}: sell {:.2f} shares at {:.2f} for ${:.2f} on date {}. Cash balance: {:.2f}".format(
                self.ticker, self.shares, self.price_history.iat[date_idx, 1], sell_value, date_idx, new_cash_balance),
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
    def __init__(self) -> None:
        self.stocks: typing.List[Stock] = []
        self.cash_balance: float = 0.0
        self.initial_cash_balance: float = 0.0

    def load_pickled_price_history(self, ticker: str) -> pd.DataFrame:
        """Read price data for this stock from a pickled file."""
        try:
            price_history = pd.read_pickle(f'../data/pickles/{ticker}.pkl')
            return price_history
        except FileNotFoundError:
            print(f"no pickle available for {ticker}; falling back to DB")
            return None

    def load_db_price_history(self, ticker: str, conn: sqlite3.Connection) -> pd.DataFrame:
        """Read price data for this stock from the DB, then pickle it for faster reference in the future."""
        sql = f"SELECT date, closing_price FROM historical_prices WHERE ticker = '{ticker}' ORDER BY date;"
        price_history = pd.read_sql(sql, conn)
        price_history.to_pickle(f'../data/pickles/{ticker}.pkl')
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
        for stock in self.stocks:
            initial_date_idx = 0
            self.cash_balance = stock.buy(initial_date_idx, self.cash_balance, self.buy_budget)

    def ramp_down(self) -> None:
        """Sell all shares of all stocks at the end of the simulation."""
        for stock in self.stocks:
            if stock.are_any_shares_owned():
                # TODO fix the sell-on date, which is currently hard-coded
                self.cash_balance = stock.sell(-1, self.cash_balance, self.buy_budget)

    def process_one_day(self, date_idx: int) -> None:
        for stock in self.stocks:
            time_to_take_gains = stock.is_above_rise_limit(date_idx, self.rise_limit)
            time_to_limit_losses = stock.is_below_sink_limit(date_idx, self.sink_limit)
            cool_off_expired = date_idx - stock.last_sell_date_idx > self.cool_off_span

            if stock.are_any_shares_owned() and (time_to_take_gains or time_to_limit_losses):
                self.cash_balance = stock.sell(date_idx, self.cash_balance, self.buy_budget)
            elif stock.are_no_shares_owned() and cool_off_expired:
                self.cash_balance = stock.buy(date_idx, self.cash_balance, self.buy_budget)

    def run_simulation(self,
                       initial_cash_balance: float,
                       buy_budget: float,
                       rise_limit: float,
                       sink_limit: float,
                       cool_off_span: int) -> None:
        """Run the time machine. This is where the magic happens."""

        # can I convert any of these into local vars?
        self.initial_cash_balance = initial_cash_balance
        self.cash_balance = initial_cash_balance
        self.buy_budget: float = buy_budget
        self.rise_limit: float = rise_limit
        self.sink_limit: float = sink_limit
        self.cool_off_span: int = cool_off_span

        self.ramp_up()
        for date_idx in range(1, len(self.stocks[0].price_history)):
            self.process_one_day(date_idx)
        self.ramp_down()

    def report_results(self, results_file_path: str) -> None:
        grand_profit = self.cash_balance - self.initial_cash_balance
        grand_percent_change = grand_profit / self.initial_cash_balance * 100

        print(f"rise_limit: {self.rise_limit}, sink_limit: {self.sink_limit}, cool off span: {self.cool_off_span}")
        print(f'initial cash balance: ${self.initial_cash_balance:.2f}')
        print(f'final cash balance: ${self.cash_balance:.0f}')
        print(f'grand amount change: ${grand_profit:.0f}')
        print(f'grand percent change: {grand_percent_change:.0f}%')

        with open(results_file_path, 'a') as results_file:
            results_file.write(f'{self.rise_limit},{self.sink_limit},{self.cool_off_span},{grand_percent_change:.0f}\n')
