import os
import pandas
import sqlite3
from termcolor import cprint
import typing


class Stock:
    ticker: str
    shares: float
    price_history: pandas.DataFrame
    last_bought_at_price: float
    last_sell_date_idx: int = 0

    def __init__(self, ticker: str, price_history: pandas.DataFrame) -> None:
        self.ticker = ticker
        self.price_history = price_history

    def is_price_history_valid(self) -> bool:
        """Determine if the price history is complete -- some stocks have only partial histories."""
        return len(self.price_history) == 1259

    def is_verbose_on(self) -> bool:
        try:
            is_verbose_on = os.environ['VERBOSE']
            return is_verbose_on.lower() == 'true'
        except:
            return False

    def buy(self, date_idx: int, cash_balance: float, buy_budget: float) -> float:
        bought_shares = buy_budget / self.price_history.iat[date_idx, 1]
        if self.is_verbose_on():
            print("{}:  buy {:.2f} shares at {:.2f} for ${:.2f} on date {}".format(
                self.ticker, bought_shares, self.price_history.iat[date_idx, 1], buy_budget, date_idx))
        self.shares = bought_shares
        cash_balance -= buy_budget
        self.last_bought_at_price = self.price_history.iat[date_idx, 1]
        return cash_balance

    def sell(self, date_idx: int, cash_balance: float, original_purchase_value: float) -> float:
        sell_value = self.shares * self.price_history.iat[date_idx, 1]
        profit_or_loss = sell_value - original_purchase_value
        if self.is_verbose_on():
            if profit_or_loss >= 0:
                text_color = 'green'
            else:
                text_color = 'red'
            cprint("{}: ${:.2f}: sell {:.2f} shares at {:.2f} for ${:.2f} on date {}".format(
                self.ticker, profit_or_loss, self.shares, self.price_history.iat[date_idx, 1], sell_value, date_idx),
                text_color)
        cash_balance += sell_value
        self.shares = 0
        self.last_sell_date_idx = date_idx
        return cash_balance

    def is_below_sink_limit(self, date_idx: int, sink_limit_percent: float) -> bool:
        if sink_limit_percent == -1:
            return False
        else:
            sink_limit_price = self.last_bought_at_price - (self.last_bought_at_price * sink_limit_percent)
            return self.price_history.iat[date_idx, 1] <= sink_limit_price

    def is_above_rise_limit(self, date_idx: int, rise_limit_percent: float) -> bool:
        if rise_limit_percent == -1:
            return False
        else:
            rise_limit_price = self.last_bought_at_price + (self.last_bought_at_price * rise_limit_percent)
            return self.price_history.iat[date_idx, 1] >= rise_limit_price

    def are_any_shares_owned(self) -> bool:
        return self.shares > 0

    def are_no_shares_owned(self) -> bool:
        return not self.are_any_shares_owned()


class Portfolio:
    stocks: typing.List[Stock] = []
    cash_balance: float = 0.0
    initial_cash_balance: float = 0.0
    buy_budget: float
    rise_limit: float
    sink_limit: float
    cool_off_span:int  # measured in days

    def load_pickled_price_history(self, ticker: str) -> pandas.DataFrame:
        try:
            price_history = pandas.read_pickle(f'../data/pickles/{ticker}.pkl')
            return price_history
        except:
            print(f"failed to read pickle for {ticker}")
            return None

    def load_db_price_history(self, ticker: str, conn: sqlite3.Connection) -> pandas.DataFrame:
        sql = f"SELECT date, closing_price FROM historical_prices WHERE ticker = '{ticker}' ORDER BY date;"
        price_history = pandas.read_sql(sql, conn)
        price_history.to_pickle(f'../data/pickles/{ticker}.pkl')
        return price_history

    def add_ticker(self, ticker: str, conn: sqlite3.Connection) -> None:
        # load price history from fast pickle (preferred) or slow DB (fallback)
        price_history = self.load_pickled_price_history(ticker)
        if type(price_history).__name__ != 'DataFrame':
            price_history = self.load_db_price_history(ticker, conn)

        # create a new Stock instance and add it to the portfolio
        stock = Stock(ticker, price_history)
        if stock.is_price_history_valid():
            self.stocks.append(stock)
            print(f"added {ticker} to portfolio")
        else:
            print(f"rejected {ticker} from portfolio because of incomplete price history")

    def ramp_up(self) -> None:
        """Buy initial shares of each stock."""
        for stock in self.stocks:
            initial_date_idx = 0
            stock.buy(initial_date_idx, self.cash_balance, self.buy_budget)

    def ramp_down(self) -> None:
        """Sell all shares of all stocks at the end of the simulation."""
        for stock in self.stocks:
            if stock.are_any_shares_owned():
                # TODO fix the sell-on date, which is currently hard-coded
                self.cash_balance = stock.sell(1200, self.cash_balance, self.buy_budget)

    def run_simulation(self,
                       initial_cash_balance: float,
                       buy_budget: float,
                       rise_limit: float,
                       sink_limit: float,
                       cool_off_span: int) -> None:
        """Run the time machine. This is where the magic happens!"""

        # can I convert any of these into local vars?
        self.initial_cash_balance = initial_cash_balance
        self.cash_balance = initial_cash_balance
        self.buy_budget = buy_budget
        self.rise_limit = rise_limit
        self.sink_limit = sink_limit
        self.cool_off_span = cool_off_span

        self.ramp_up()

        for date_idx in range(1, len(self.stocks[0].price_history)):
            for stock in self.stocks:
                time_to_take_gains = stock.is_above_rise_limit(date_idx, self.rise_limit)
                time_to_limit_losses = stock.is_below_sink_limit(date_idx, self.sink_limit)
                cool_off_expired = date_idx - stock.last_sell_date_idx >= self.cool_off_span

                if stock.are_any_shares_owned() and (time_to_take_gains or time_to_limit_losses):
                    self.cash_balance = stock.sell(date_idx, self.cash_balance, self.buy_budget)
                elif stock.are_no_shares_owned() and cool_off_expired:
                    self.cash_balance = stock.buy(date_idx, self.cash_balance, self.buy_budget)

        self.ramp_down()

    def print_parms(self) -> None:
        print(f"rise_limit: {self.rise_limit}, sink_limit: {self.sink_limit}, cool off span: {self.cool_off_span}")

    def print_final_stats(self) -> None:
        grand_profit = self.cash_balance - self.initial_cash_balance
        grand_percent_change = grand_profit / self.initial_cash_balance * 100

        print("initial cash balance: ${:.2f}".format(self.initial_cash_balance))
        print("final cash balance: ${:.0f}".format(self.cash_balance))
        print("final amount change:: ${:.0f}".format(grand_profit))
        print("final percent change: {:.0f}%".format(grand_percent_change))
