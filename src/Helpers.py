import os
import sqlite3
import typing


def get_all_tickers(conn: sqlite3.Connection) -> typing.List:
    """Extract all ticker symbols from the DB."""
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT ticker FROM historical_prices;')
    tickers = []
    rows = cursor.fetchall()
    for row in rows:
        ticker = row[0]
        tickers.append(ticker)
    cursor.close()
    if is_limit_tickers_on():
        return tickers[:5]
    else:
        return tickers


def is_limit_tickers_on() -> bool:
    """If the user sets the LIMIT_TICKERS env var to true, load only 5 tickers."""
    return get_bool_env_var('LIMIT_TICKERS')


def is_verbose_on() -> bool:
    """If the user sets the VERBOSE env var to true, print all transactions."""
    return get_bool_env_var('VERBOSE')


def get_bool_env_var(env_var: str) -> bool:
    """Return the value of a BOOLEAN environment var."""
    try:
        value = os.environ[env_var]
        return value.lower() == 'true'
    except KeyError:
        return False


def prep_results_file(file_path: str) -> None:
    """Create a file to put our results in, and add CSV headers to it."""
    with open(file_path, 'w') as results_file:
        results_file.write('RISE LIMIT,SINK LIMIT,COOL-OFF SPAN,GRAND PERCENT CHANGE\n')
