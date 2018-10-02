import pandas
import sqlite3
from termcolor import cprint


class Stock:
    ticker = None
    shares = 0.0
    price_history = None
    last_bought_at_price = 0.0
    last_sell_date_idx = 0

    def __init__(self, ticker, price_history):
        self.ticker = ticker
        self.price_history = price_history

    def buy(self, date_idx: int, cash_balance: float, buy_budget: float) -> float:
        bought_shares = buy_budget / self.price_history.iat[date_idx, 1]
        print("{}:  buy {:.2f} shares at {:.2f} for ${:.2f} on date {}".format(
            self.ticker, bought_shares, self.price_history.iat[date_idx, 1], buy_budget, date_idx))
        self.shares = bought_shares
        cash_balance -= buy_budget
        self.last_bought_at_price = self.price_history.iat[date_idx, 1]
        return cash_balance

    def sell(self, date_idx: int, cash_balance: float, original_purchase_value: float) -> float:
        sell_value = self.shares * self.price_history.iat[date_idx, 1]
        profit_or_loss = sell_value - original_purchase_value

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
        sink_limit_price = self.last_bought_at_price - (self.last_bought_at_price * sink_limit_percent)
        return self.price_history.iat[date_idx, 1] <= sink_limit_price

    def is_above_rise_limit(self, date_idx: int, rise_limit_percent: float) -> bool:
        rise_limit_price = self.last_bought_at_price + (self.last_bought_at_price * rise_limit_percent)
        return self.price_history.iat[date_idx, 1] >= rise_limit_price

    def are_any_shares_owned(self) -> bool:
        return self.shares > 0

    def are_no_shares_owned(self) -> bool:
        return not self.are_any_shares_owned()


class Portfolio:
    stocks = []
    cash_balance = 0.0
    initial_cash_balance = 0.0
    buy_budget = 0.0
    rise_limit = 0.0
    sink_limit = 0.0
    cool_off_span = 3  # measured in days

    def __init__(self, initial_cash_balance, buy_budget, rise_limit, sink_limit, cool_off_span):
        self.initial_cash_balance = initial_cash_balance
        self.cash_balance = initial_cash_balance
        self.buy_budget = buy_budget
        self.rise_limit = rise_limit
        self.sink_limit = sink_limit
        self.cool_off_span = cool_off_span

    def add_ticker(self, ticker: str) -> None:
        # open DB
        conn = sqlite3.connect('../data/SandP500.sqlite3')
        cursor = conn.cursor()

        # load price history from DB into a pandas dataframe
        sql = f"SELECT date, closing_price FROM historical_prices WHERE ticker = '{ticker}' ORDER BY date;"
        price_history = pandas.read_sql(sql, conn)

        # close DB
        cursor.close()
        conn.close()

        # create a new Stock instance and add it to the portfolio
        new_stock = Stock(ticker, price_history)
        self.stocks.append(new_stock)
        print(f"added {ticker} to portfolio")

    def ramp_up(self) -> None:
        """Buy initial shares of each stock."""
        for stock in self.stocks:
            initial_date_idx = 0
            stock.buy(initial_date_idx, self.cash_balance, self.buy_budget)

    def run_simulation(self) -> None:
        """Run the time machine. This is where the magic happens!"""
        for date_idx in range(1, len(self.stocks[0].price_history)):
            for stock in self.stocks:
                time_to_take_gains = stock.is_above_rise_limit(date_idx, self.rise_limit)
                time_to_limit_losses = stock.is_below_sink_limit(date_idx, self.sink_limit)
                cool_off_expired = date_idx - stock.last_sell_date_idx >= self.cool_off_span

                if stock.are_any_shares_owned() and (time_to_take_gains or time_to_limit_losses):
                    self.cash_balance = stock.sell(date_idx, self.cash_balance, self.buy_budget)
                elif stock.are_no_shares_owned() and cool_off_expired:
                    self.cash_balance = stock.buy(date_idx, self.cash_balance, self.buy_budget)

    def ramp_down(self) -> None:
        """Sell all shares of all stocks at the end of the simulation."""
        for stock in self.stocks:
            if stock.are_any_shares_owned():
                self.cash_balance = stock.sell(9, self.cash_balance, self.buy_budget)

    def print_initial_stats(self) -> None:
        """Print info about the portfolio before any trades happen."""
        print("initial cash balance: ${:.2f}\n".format(self.initial_cash_balance))

    def print_final_stats(self) -> None:
        grand_profit = self.cash_balance - self.initial_cash_balance
        grand_percent_change = grand_profit / self.initial_cash_balance * 100

        print()
        print("final cash balance: ${:.0f}".format(self.cash_balance))
        print("final amount change:: ${:.0f}".format(grand_profit))
        print("final percent change: {:.0f}%".format(grand_percent_change))
