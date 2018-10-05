import Models
import os
import sqlite3


# TODO MOVE THIS
def is_limit_tickers_on() -> bool:
    try:
        limit_tickers = os.environ['LIMIT_TICKERS']
        return limit_tickers.lower() == 'true'
    except:
        return False

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
portfolio = Models.Portfolio()

if is_limit_tickers_on():
    tickers = tickers[:5]

for ticker in tickers:
    portfolio.add_ticker(ticker, conn)

# close DB
cursor.close()
conn.close()

rise_limits = [.1, .96]
# rise_limits = [.02, .04, .06, .08, .1,
#                .12, .14, .16, .18, .2,
#                .22, .24, .26, .28, .3,
#                .32, .34, .36, .38, .4,
#                .42, .44, .46, .48, .5,
#                .52, .54, .56, .58, .6,
#                .62, .64, .66, .68, .7,
#                .72, .74, .76, .78, .8,
#                .82, .84, .86, .88, .9,
#                .92, .94, .96, .98]

for rise_limit in rise_limits:
    print("-----")
    portfolio.run_simulation(initial_cash_balance, buy_budget, rise_limit, sink_limit, cool_off_span)
    portfolio.print_parms()
    portfolio.print_final_stats()


# Buy and hold for five years
print("-----")
portfolio.run_simulation(initial_cash_balance, buy_budget, -1, -1, 0)
portfolio.print_parms()
portfolio.print_final_stats()
