import sqlite3

import numpy as np
import pandas as pd
from behave import *

import data.LoadDatabase
from src import Models

CSV_FILE_PATH = 'test/resources/test.csv'
DB_FILE_PATH = 'test/resources/test.sqlite3'


# --- GIVENs ---

@given('a CSV file containing historical stock data')
def step_impl(context):
    historical_prices = [
        'DATE,OPENING_PRICE,LOW_PRICE,HIGH_PRICE,CLOSING_PRICE,VOLUME,TICKER',
        'date1,x,x,x,12.42,x,FOO',
        'date2,x,x,x,100.2,x,BAR']
    historical_prices_csv = open(CSV_FILE_PATH, 'w')
    for historical_price in historical_prices:
        historical_prices_csv.write(historical_price + '\n')
    historical_prices_csv.close()


@given("the simulation buys a stock that's declining in price")
def step_impl(context):
    price_history = pd.DataFrame({'DATE': np.array(['date0', 'date1']),
                                  'PRICE': pd.Categorical([10.0, 9.0]),
                                  'TICKER': 'FOO'})
    portfolio = Models.Portfolio(buy_budget=1000.0)
    portfolio.add_ticker(ticker='FOO',
                         required_num_historical_prices=-1,
                         conn=None,
                         price_history=price_history)
    context.portfolio = portfolio


@given("the simulation buys a stock that's rising in price")
def step_impl(context):
    price_history = pd.DataFrame({'DATE': np.array(['date0', 'date1', 'date2']),
                                  'PRICE': pd.Categorical([10.0, 10.9, 12.0]),
                                  'TICKER': 'FOO'})

    portfolio = Models.Portfolio(buy_budget=1000.0)
    portfolio.add_ticker(ticker='FOO',
                         required_num_historical_prices=-1,
                         conn=None,
                         price_history=price_history)
    context.portfolio = portfolio


@given('the simulation sells a stock')
def step_impl(context):
    price_history = pd.DataFrame({'DATE': np.array(['date0', 'date1', 'date2', 'date3', 'date4', 'date5', 'date6']),
                                  'PRICE': pd.Categorical([10.0, 12.0, 20.0, 20.0, 20.0, 20.0, 21.0]),
                                  'TICKER': 'FOO'})

    portfolio = Models.Portfolio(buy_budget=1000.0)
    portfolio.add_ticker(ticker='FOO',
                         required_num_historical_prices=-1,
                         conn=None,
                         price_history=price_history)
    context.portfolio = portfolio


@given('stocks that fluctuate in price over time')
def step_impl(context):
    # When running simulator, set parms: rise_limit=0.15, sink_limit=0.03, cool_off_span=2
    # initial cash balance = $2000

    # FOO
    # date0: buy 100 shares at $10. Cash balance = $0
    # date1: hold
    # date2: sell 100 shares at $12. Cash balance = $1200
    # date3: cool off
    # date4: cool off
    # date5: buy 111.11 shares at $9. Cash balance = $200
    # date6: sell 111.1 shares at $8. Cash balance = $1088.80
    # date7: cool off
    # date8: cool off
    # date9: buy 200 shares at $5. Cash balance = $88.80
    # date10: hold
    # date11: auto-sell 200 shares at $4. Cash balance = $888.8
    price_history_foo = pd.DataFrame({'DATE': np.array(['date0', 'date1', 'date2', 'date3', 'date4', 'date5',
                                                        'date6', 'date7', 'date8', 'date9', 'date10', 'date11']),
                                      'PRICE': pd.Categorical([10.0, 11.0, 12.0, 4.0, 30.0, 9.0,
                                                               8.0, 1.0, 100.0, 5.0, 5.1, 4.0]),
                                      'TICKER': 'FOO'})

    # BAR
    # date0: buy 100 shares at $10. Cash balance = $0
    # date1: sell 100 shares at $8. Cash balance = $800
    # date2: cool off
    # date3: cool off
    # date4: buy 10 shares at $100. Cash balance = $-200
    # date5: hold
    # date6: sell 10 shares at $90. Cash balance = $700
    # date7: cool off
    # date8: cool off
    # date9: buy 20 shares at $50. Cash balance = $-300
    # date10: hold
    # date11: auto-sell 20 shares at $100. Cash balance = $1700
    price_history_bar = pd.DataFrame({'DATE': np.array(['date0', 'date1', 'date2', 'date3', 'date4', 'date5',
                                                        'date6', 'date7', 'date8', 'date9', 'date10', 'date11']),
                                      'PRICE': pd.Categorical([10.0, 8.0, 1.0, 100.0, 100.0, 102.0,
                                                               90.0, 200.0, 1.0, 50.0, 51.0, 100.0]),
                                      'TICKER': 'BAR'})

    portfolio = Models.Portfolio(buy_budget=1000.0)
    portfolio.add_ticker(ticker='FOO',
                         required_num_historical_prices=-1,
                         conn=None,
                         price_history=price_history_foo)
    portfolio.add_ticker(ticker='BAR',
                         required_num_historical_prices=-1,
                         conn=None,
                         price_history=price_history_bar)
    context.portfolio = portfolio


# --- WHENs ---

@when('the DB load tool runs against that CSV file')
def step_impl(context):
    data.LoadDatabase.main(CSV_FILE_PATH, DB_FILE_PATH)


@when("that stock's price sinks below a sink limit")
def step_impl(context):
    context.portfolio.process_all_days(rise_limit=15,
                                       sink_limit=3,
                                       cool_off_span=30)


@when("that stock's price rises above a rise limit")
def step_impl(context):
    context.portfolio.process_all_days(rise_limit=15,
                                       sink_limit=3,
                                       cool_off_span=30)


@when('the cool-off period has passed')
def step_impl(context):
    context.portfolio.process_all_days(rise_limit=15,
                                       sink_limit=3,
                                       cool_off_span=3)


@when('the simulation completes')
def step_impl(context):
    context.portfolio.process_all_days(rise_limit=15,
                                       sink_limit=3,
                                       cool_off_span=2)


# --- THENs ---

@then('the tool creates a DB containing that historical stock data')
def step_impl(context):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    sql = "SELECT * FROM historical_prices;"
    cursor.execute(sql)

    rows = cursor.fetchall()
    assert rows[0] == (1, 'date1', 'FOO', 12.42)
    assert rows[1] == (2, 'date2', 'BAR', 100.2)

    cursor.close()
    conn.close()


@then('the simulation sells that stock to prevent further losses')
def step_impl(context):
    actual_cash_balance = context.portfolio.cash_balance
    expected_cash_balance = 900.0
    assert (actual_cash_balance == expected_cash_balance), \
        f"expected cash balance: {expected_cash_balance}, actual cash balance: {actual_cash_balance}"


@then('the simulation sells that stock to take profits')
def step_impl(context):
    expected_cash_balance = 1200.0
    actual_cash_balance = context.portfolio.cash_balance
    assert (actual_cash_balance == expected_cash_balance), \
        f"expected cash balance: {expected_cash_balance}, actual cash balance: {actual_cash_balance}"


@then('the simulation buys that stock again')
def step_impl(context):
    expected_cash_balance = 1250.0
    actual_cash_balance = context.portfolio.cash_balance
    assert (actual_cash_balance == expected_cash_balance), \
        f"expected cash balance: {expected_cash_balance}, actual cash balance: {actual_cash_balance}"


@then('the simulation calculates the grand loss or profit of all trades on all stocks')
def step_impl(context):
    expected_cash_balance = 2588.89
    actual_cash_balance = round(context.portfolio.cash_balance, 2)
    assert (actual_cash_balance == expected_cash_balance), \
        f"expected cash balance: {expected_cash_balance}, actual cash balance: {actual_cash_balance}"
