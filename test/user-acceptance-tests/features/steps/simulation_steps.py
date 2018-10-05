from behave import *
from data.LoadDatabase import main
import sqlite3

csv_file_path = 'test/user-acceptance-tests/resources/test.csv'
db_file_path = 'test/user-acceptance-tests/resources/test.sqlite3'

@given('a CSV file containing historical stock data')
def step_impl(context):
    test_historical_prices = [
        'DATE,OPENING_PRICE,LOW_PRICE,HIGH_PRICE,CLOSING_PRICE,VOLUME,TICKER',
        'date1,x,x,x,12.42,x,foo',
        'date2,x,x,x,100.2,x,bar']
    test_csv = open(csv_file_path, 'w')
    for test_historical_price in test_historical_prices:
        test_csv.write(test_historical_price + '\n')
    test_csv.close()



@when('the DB load tool runs against that CSV file')
def step_impl(context):
    main(csv_file_path, db_file_path)


@then('the tool creates a DB containing that historical stock data')
def step_impl(context):
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()

    sql = "SELECT * FROM historical_prices;"
    cursor.execute(sql)

    rows = cursor.fetchall()
    assert rows[0] == (1, 'date1', 'foo', 12.42)
    assert rows[1] == (2, 'date2', 'bar', 100.2)

    cursor.close()
    conn.close()
