Feature: simulate stock transactions

  # scenarios related to the trading algorithm

  Scenario: sell a stock when its price sinks below a limit
    Given the simulation buys a stock that's declining in price
    When that stock's price sinks below a sink limit
    Then the simulation sells that stock to prevent further losses

  Scenario: sell a stock when its price rises above a limit
    Given the simulation buys a stock that's rising in price
    When that stock's price rises above a rise limit
    Then the simulation sells that stock to take profits

  Scenario: after selling a stock, wait a bit and then buy it back
    Given the simulation sells a stock
    When the cool-off period has passed
    Then the simulation buys that stock again

  Scenario: report grand loss or profit
    Given stocks that fluctuate in price over time
    When the simulation completes
    Then the simulation calculates the grand loss or profit of all trades on all stocks


  # scenarios related to simulation plumbing and NOT the trading algorithm

  Scenario: load CSV data into a DB for future processing
    Given a CSV file containing historical stock data
    When the DB load tool runs against that CSV file
    Then the tool creates a DB containing that historical stock data

