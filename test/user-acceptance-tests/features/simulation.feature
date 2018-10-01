Feature: simulate stock transactions in the past

  Scenario: load CSV data into a db for future processing
    Given a CSV file containing historical stock data
    When the DB load tool runs against that CSV file
    Then the tool creates a DB containing that historical stock data


