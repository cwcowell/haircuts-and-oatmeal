from behave import *


@given('a CSV file containing historical stock data')
def step_impl(context):
    print("pending")
    assert False


@when('the DB load tool runs against that CSV file')
def step_impl(context):
    print("pending")
    assert False


@then('the tool creates a DB containing that historical stock data')
def step_impl(context):
    print("pending")
    assert context.failed is False
