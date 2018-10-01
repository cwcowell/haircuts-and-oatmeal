import Models
import sqlite3


def clean_tickers(tickers: list) -> list:
    """Delete any ticker that doesn't have a full set of price histories."""
    # TODO
    return tickers


# --- CONSTANTS ---

buy_budget = 1000.0  # how much we spend on any stock when buying it

rise_limit = 0.1  # how high a stock can rise before we sell it, to take profits
sink_limit = 0.05  # how far a stock can sink before we sell it, to protect against further losses
cool_off_span = 3  # how long to wait after selling a stock, before automatically buying that stock again

# def load_single_ticker_price_history(ticker):
#     path = 'datasets/SandP500/individual_stocks_5yr/{}_data.csv'.format(ticker)
#     file = open(path, 'r')
#     file.readline()  # throw away the header row
#     prices = []
#     for line in file:
#         line_parts = line.split(',')
#         closing_price = float(line_parts[4])
#         prices.append(closing_price)
#     return prices
#
#
# price_histories = dict()
# for s_and_p_ticker in s_and_p_tickers:
#     price_histories[s_and_p_ticker] = load_single_ticker_price_history(s_and_p_ticker)


# # --- CREATE STOCKS ---
# abt_stock = Models.Stock('ABT', price_histories['ABT'])
# mmm_stock = Models.Stock('MMM', price_histories['MMM'])
# stocks = [abt_stock, mmm_stock]


# --- CREATE PORTFOLIO ---

# open DB
conn = sqlite3.connect('../data/SandP500.sqlite3')
cursor = conn.cursor()

# get ticker symbols
sql = 'SELECT DISTINCT ticker FROM historical_prices;'
cursor.execute(sql)
tickers = []
for row in cursor:
    tickers.append(row[0])

# close DB
cursor.close()
conn.commit()
conn.close()

tickers = clean_tickers(tickers)

# add each stock to portfolio
initial_cash_balance = buy_budget * len(tickers)
portfolio = Models.Portfolio(initial_cash_balance)
for ticker in tickers:
    portfolio.add_ticker(ticker)


# --- MAIN LOGIC ---

print("initial cash balance: ${:.2f}\n".format(portfolio.cash_balance))

grand_profit = portfolio.cash_balance - initial_cash_balance
grand_percent_change = grand_profit / initial_cash_balance * 100

print("\nfinal cash balance: ${:.0f}".format(portfolio.cash_balance))
print("final amount change:: ${:.0f}".format(grand_profit))
print("final percent change: {:.0f}%".format(grand_percent_change))
