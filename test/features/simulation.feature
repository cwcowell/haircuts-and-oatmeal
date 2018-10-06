#noinspection CucumberUndefinedStep
Feature: simulate stock transactions in the past

#  Scenario: load CSV data into a db for future processing
#    Given a CSV file containing historical stock data
#    When the DB load tool runs against that CSV file
#    Then the tool creates a DB containing that historical stock data

  Scenario: sell a stock when its price sinks below some limit
    Given the simulation buys a certain stock
    When that stock's price sinks below a sink limit
    Then the simulation sells that stock

#  Scenario: sell a stock when its price rises above some limit
#    Given the simulation buys a certain stock
#    When that stock's price rises above a rise limit
#    Then the simulation sells that stock
#
#  Scenario: after selling a stock, wait a bit and then buy it back
#    Given the simulation sells a stock
#    When the cool-off period has passed
#    Then the simulation buys that stock again
#
#  Scenario: report grand loss or profit
#    When the simulation completes
#    Then the simulation reports the grand loss or profit of all trades
