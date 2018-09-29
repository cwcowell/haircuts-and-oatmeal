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
    stocks = None
    cash_balance = 0.0

    def __init__(self, initial_cash_balance, stocks):
        self.cash_balance = initial_cash_balance
        self.stocks = stocks

    def __str__(self):
        output = "cash balance: {}\n".format(self.cash_balance)
        for stock in self.stocks:
            # output += "ticker: {}, shares: {}\n".format(stock.ticker, stock.shares)
            output += str(stock) + "\n"
        return output
