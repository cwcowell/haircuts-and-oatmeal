from behave import *
import sys
print(sys.path)
from .. .. ..data import load_database


@given('a CSV file containing historical stock data')
def step_impl(context):
    data = ['Oslo, Norway', 'Stockholm, Sweden', 'Copenhagen, Denmark']
    test_csv = open('test.csv', 'w')
    test_csv.writelines(data)
    test_csv.close()


@when('the DB load tool runs against that CSV file')
def step_impl(context):
    csv_file_path = 'test.csv'
    db_file_path = 'test.sqlite3'
    load_database.main(csv_file_path, db_file_path)


@then('the tool creates a DB containing that historical stock data')
def step_impl(context):
    pass
