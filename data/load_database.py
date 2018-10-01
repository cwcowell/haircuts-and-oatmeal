#!/usr/bin/env python3

""" The docstring of a script (a stand-alone program) should be usable as its "usage" message, printed when the script is invoked with incorrect or missing arguments (or perhaps with a "-h" option, for "help"). Such a docstring should document the script's purpose, command line parameters and any dependencies. Usage messages can be fairly elaborate (several screens full) and should be sufficient for a new user to use the script properly, as well as provide a complete quick reference to all options and arguments for the sophisticated user.

Add help message about how the CC0-licensed dataset can be downloaded from Kraggle, and give the URL
"""

import os
import sqlite3


def delete_file(file_path: str) -> None:
    """Delete a file, if it exists."""
    if os.path.exists(file_path):
        os.remove(file_path)


def connect(db_file: str) -> sqlite3.Connection:
    """Connect to a SQLite database."""
    conn = sqlite3.connect(db_file)
    return conn


def create_historical_prices_table(cursor: sqlite3.Cursor) -> None:
    """Create a SQLite table using the provided connection."""
    sql = "CREATE TABLE historical_prices(" \
          "price_id integer PRIMARY KEY, " \
          "date string NOT NULL, " \
          "ticker string NOT NULL, " \
          "closing_price float NOT NULL);"
    cursor.execute(sql)


def insert_historical_price(cursor: sqlite3.Cursor,
                            date: str,
                            ticker: str,
                            closing_price: float) -> None:
    """TODO docstring"""
    sql = f"INSERT INTO historical_prices(date, ticker, closing_price) VALUES('{date}', '{ticker}', {closing_price})"
    cursor.execute(sql)


def convert_csv_file_to_db(cursor: sqlite3.Cursor, csv_file_path: str) -> None:
    """TODO docstring"""
    file = open(csv_file_path, 'r')
    file.readline()  # throw away the header row
    for line in file:
        add_csv_line_to_db(cursor, line)


def add_csv_line_to_db(cursor: sqlite3.Cursor, csv_line: str) -> None:
    """TODO docstring"""
    csv_line_parts = csv_line.split(',')
    date = csv_line_parts[0]
    closing_price = float(csv_line_parts[4])
    ticker = csv_line_parts[6].strip()
    insert_historical_price(cursor, date, ticker, closing_price)


def main() -> None:
    """TODO docstring"""
    print("This could take up to 30 seconds on a slow computer.")

    csv_file_path = 'datasets/SandP500/all_stocks_5yr.csv'
    db_file_path = 'SandP500.sqlite3'

    delete_file(db_file_path)

    conn = connect(db_file_path)
    cursor = conn.cursor()

    create_historical_prices_table(cursor)
    convert_csv_file_to_db(cursor, csv_file_path)

    cursor.close()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
