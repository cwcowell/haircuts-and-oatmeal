import os
import sqlite3
import typing


def get_all_tickers(conn: sqlite3.Connection) -> typing.List:
    """Extract all ticker symbols from the DB."""
    cursor = conn.cursor()
    sql = 'SELECT DISTINCT ticker FROM historical_prices;'
    cursor.execute(sql)
    tickers = []
    all_rows = cursor.fetchall()
    for row in all_rows:
        ticker = row[0]
        tickers.append(ticker)
    cursor.close()
    if is_limit_tickers_on():
        return tickers[:5]
    else:
        return tickers


def is_limit_tickers_on() -> bool:
    """If the user sets the LIMIT_TICKERS env var to true, load only 5 tickers."""
    try:
        limit_tickers = os.environ['LIMIT_TICKERS']
        return limit_tickers.lower() == 'true'
    except:
        return False


def is_verbose_on() -> bool:
    """If the user sets the VERBOSE env var to true, print all transactions."""
    try:
        is_verbose_on = os.environ['VERBOSE']
        return is_verbose_on.lower() == 'true'
    except:
        return False


def prep_results_file(file_path) -> None:
    """Create a file to put our results in, and write CSV headers in it."""
    with open(file_path, 'w') as results_file:
        results_file.write('RISE LIMIT,SINK LIMIT,COOL-OFF SPAN,GRAND % CHANGE\n')
