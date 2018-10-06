from behave import *
from data.LoadDatabase import main
import pandas as pd
from src import Models
import sqlite3

CSV_FILE_PATH = 'test/resources/test.csv'
DB_FILE_PATH = 'test/resources/test.sqlite3'


@given('a CSV file containing historical stock data')
def step_impl(context):
    historical_prices = [
        'DATE,OPENING_PRICE,LOW_PRICE,HIGH_PRICE,CLOSING_PRICE,VOLUME,TICKER',
        'date1,x,x,x,12.42,x,foo',
        'date2,x,x,x,100.2,x,bar']
    historical_prices_csv = open(CSV_FILE_PATH, 'w')
    for historical_price in historical_prices:
        historical_prices_csv.write(historical_price + '\n')
    historical_prices_csv.close()


@given('the simulation buys a certain stock')
def step_impl(context):
    prices = ['date1,10.0,foo',
              'date2,11.0,foo',
              'date3,12.0,foo',
              'date4,200.0,foo']
    price_history_csv = open(CSV_FILE_PATH, 'w')
    for price in prices:
        price_history_csv.write(price + '\n')
    price_history_csv.close()

    price_history_df = pd.read_csv(CSV_FILE_PATH)

    portfolio = Models.Portfolio()
    portfolio.add_ticker(ticker='foo', conn=None, price_history=price_history_df, test_mode=True)
    portfolio.run_simulation(initial_cash_balance=1000.0,
                             buy_budget=1000.0,
                             rise_limit=0.15,
                             sink_limit=0.03,
                             cool_off_span=3)
    assert (portfolio.cash_balance == 1200.0), f"actual cash balance: {portfolio.cash_balance}"


@when('the DB load tool runs against that CSV file')
def step_impl(context):
    main(CSV_FILE_PATH, DB_FILE_PATH)


@then('the tool creates a DB containing that historical stock data')
def step_impl(context):
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()

    sql = "SELECT * FROM historical_prices;"
    cursor.execute(sql)

    rows = cursor.fetchall()
    assert rows[0] == (1, 'date1', 'foo', 12.42)
    assert rows[1] == (2, 'date2', 'bar', 100.2)

    cursor.close()
    conn.close()
