import pandas
import sqlite3
from termcolor import cprint


class Stock:
    ticker = None
    shares = 0.0
    price_history = None
    bought_at_price = 0.0
    last_sell_date = 0

    def __init__(self, ticker, price_history):
        self.ticker = ticker
        self.price_history = price_history

    def __str__(self):
        return "ticker: {}, shares: {}, bought_at_price: {}".format(
            self.ticker, self.shares, self.bought_at_price)

    def buy(self, date, cash_balance, buy_budget):
        bought_shares = buy_budget / self.price_history[date]
        print("{}:  buy {:.2f} shares at {:.2f} for ${:.2f} on date {}".format(
            self.ticker, bought_shares, self.price_history[date], buy_budget, date))
        self.shares = bought_shares
        cash_balance -= buy_budget
        self.bought_at_price = self.price_history[date]
        return cash_balance

    def sell(self, date, cash_balance, original_purchase_value):
        sell_value = self.shares * self.price_history[date]
        profit_or_loss = sell_value - original_purchase_value

        if profit_or_loss >= 0:
            text_color = 'green'
        else:
            text_color = 'red'

        cprint("{}: ${:.2f}: sell {:.2f} shares at {:.2f} for ${:.2f} on date {}".format(
            self.ticker, profit_or_loss, self.shares, self.price_history[date], sell_value, date),
            text_color)
        cash_balance += sell_value
        self.shares = 0
        self.last_sell_date = date
        return cash_balance

    def is_below_sink_limit(self, date, sink_limit_percent):
        sink_limit_price = self.bought_at_price - (self.bought_at_price * sink_limit_percent)
        return self.price_history[date] <= sink_limit_price

    def is_above_rise_limit(self, date, rise_limit_percent):
        rise_limit_price = self.bought_at_price + (self.bought_at_price * rise_limit_percent)
        return self.price_history[date] >= rise_limit_price

    def are_any_shares_owned(self):
        return self.shares > 0

    def are_no_shares_owned(self):
        return not self.are_any_shares_owned()


class Portfolio:
    stocks = []
    cash_balance = 0.0
    initial_cash_balance = 0.0

    def __init__(self, initial_cash_balance):
        self.initial_cash_balance = initial_cash_balance
        self.cash_balance = initial_cash_balance

    def add_ticker(self, ticker: str) -> None:
        # open DB
        conn = sqlite3.connect('../data/SandP500.sqlite3')
        cursor = conn.cursor()

        # get price history into pandas dataframe
        sql = f"SELECT (ticker, date, closing_price) FROM historical_prices WHERE ticker = '{ticker}' ORDER BY date;"
        dataframe = pandas.read_sql(sql, conn)


        # cursor.execute(sql)
        ticker_prices = []
        # for row in cursor:
        #     ticker_price = dict()
        #     ticker_price['ticker']
        #     ticker_prices.append(row)

        # close DB
        cursor.close()
        conn.commit()
        conn.close()
        stock = Stock(ticker)


    def ramp_up(self) -> None:
        """ buy initial shares of each stock """
        for stock in self.stocks:
            initial_date_idx = 0
            stock.buy(initial_date_idx, self.cash_balance, buy_budget)

    def run_simulation(self) -> None:
        """ actually run the time machine """
        for date_idx in range(1, len(self.stocks[0].price_history)):
            for stock in self.stocks:
                time_to_take_gains = stock.is_above_rise_limit(date_idx, rise_limit)
                time_to_limit_losses = stock.is_below_sink_limit(date_idx, sink_limit)
                cool_off_expired = date_idx - stock.last_sell_date >= cool_off_span

                if stock.are_any_shares_owned() and (time_to_take_gains or time_to_limit_losses):
                    self.cash_balance = stock.sell(date_idx, self.cash_balance, buy_budget)
                elif stock.are_no_shares_owned() and cool_off_expired:
                    self.cash_balance = stock.buy(date_idx, self.cash_balance, buy_budget)

    def ramp_down(self) -> None:
        """ sell all shares of all stocks at the end of the simulation """
        for stock in self.stocks:
            if stock.are_any_shares_owned():
                self.cash_balance = stock.sell(9, self.cash_balance, buy_budget)
