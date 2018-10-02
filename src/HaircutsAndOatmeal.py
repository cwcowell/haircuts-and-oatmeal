import Models
import sqlite3


buy_budget = 1000.0  # how much we spend on any stock when buying it
rise_limit = 0.15  # how high a stock can rise before we sell it, to take profits
sink_limit = 0.05  # how far a stock can sink before we sell it, to protect against further losses
cool_off_span = 10  # how long to wait after selling a stock, before automatically buying that stock again

# open DB
conn = sqlite3.connect('../data/SandP500.sqlite3')
cursor = conn.cursor()

# get list of all ticker symbols
sql = 'SELECT DISTINCT ticker FROM historical_prices;'
cursor.execute(sql)
tickers = []
for row in cursor:
    tickers.append(row[0])

# add each stock to portfolio
initial_cash_balance = buy_budget * len(tickers)
portfolio = Models.Portfolio(initial_cash_balance, buy_budget, rise_limit, sink_limit, cool_off_span)

for ticker in tickers:
    portfolio.add_ticker(ticker, conn)

# close DB
cursor.close()
conn.close()

portfolio.print_initial_stats()
portfolio.run_simulation()
portfolio.print_final_stats()
