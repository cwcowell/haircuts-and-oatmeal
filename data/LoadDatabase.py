#!/usr/bin/env python3

"""usage: ./LoadDatabase.py <csv_file_path> <db_file_path>

Load all information from the original S&P 500 source CSV file into a SQLite3 DB.
This is intended to be used with the S&P 500 CSV downloaded from Kaggle at https://www.kaggle.com/camnugent/sandp500.
This Kaggle CSV file is released under the CC0 license.
"""

import os
import sqlite3
import sys
import typing


def delete_file(file_path: str) -> None:
    """Delete a file, if it exists."""
    if os.path.exists(file_path):
        os.remove(file_path)


def connect_db(db_file_path: str) -> (sqlite3.Connection, sqlite3.Cursor):
    """Connect to a SQLite database."""
    delete_file(db_file_path)
    conn = sqlite3.connect(db_file_path)
    cursor = conn.cursor()
    return conn, cursor


def disconnect_db(conn: sqlite3.Connection, cursor: sqlite3.Cursor) -> None:
    """Safely close down a connection to a DB"""
    cursor.close()
    conn.commit()
    conn.close()


def create_historical_prices_table(cursor: sqlite3.Cursor) -> None:
    """Create a SQLite3 table using the provided connection."""
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
    """Add a single historical price to the DB."""
    sql = "INSERT INTO historical_prices(date, ticker, closing_price) " \
          f"VALUES('{date}', '{ticker}', {closing_price})"
    cursor.execute(sql)


def convert_csv_file_to_db(cursor: sqlite3.Cursor, csv_file_path: str) -> None:
    """Copy S&P 500 info from a Kaggle CSV to a SQLite3 DB."""
    with open(csv_file_path, 'r') as csv_file:
        csv_file.readline()  # throw away the CSV's header row
        for line in csv_file:
            add_csv_line_to_db(cursor, line)


def add_csv_line_to_db(cursor: sqlite3.Cursor, csv_line: str) -> None:
    """Parse a single CSV line and insert it a SQLite3 DB."""
    csv_line_parts: typing.List[str] = csv_line.split(',')
    date: str = csv_line_parts[0].strip()
    closing_price: float = float(csv_line_parts[4].strip())
    ticker: str = csv_line_parts[6].strip()
    insert_historical_price(cursor, date, ticker, closing_price)


def main(csv_file_path: str, db_file_path: str) -> None:
    """Copy S&P 500 info from a Kaggle CSV to a SQLite3 DB."""
    print("This takes up to 30 seconds on a slow computer.")
    (conn, cursor) = connect_db(db_file_path)
    create_historical_prices_table(cursor)
    convert_csv_file_to_db(cursor, csv_file_path)
    disconnect_db(conn, cursor)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        exit(1)
    csv_file_path: str = sys.argv[1]
    db_file_path: str = sys.argv[2]
    main(csv_file_path, db_file_path)
