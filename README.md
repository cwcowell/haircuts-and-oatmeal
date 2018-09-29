# Haircuts and Oatmeal

This is an **extremely simple** algorithmic trading program. It doesn't actually trade; it's just a tool for figuring out how well the world's most basic trading algorithm *would have* worked, using historical pricing data.

The name is a highly bastardized version of a concept from a Shel Silverstein poem, in which he claims "Daddy spends all his money on haircuts and oatmeal." I'm probably remembering that 98% wrong, but it's become a family meme around my house.


### Author

Chris Cowell


### To Do

* Change how stocks are created so you can use `stocks.append(Stock('AAPL'))` and it will auto-load the data
* Store historical data with SQLite
* Add unit tests
* Add Cucumber user acceptance tests
* Add comparison data to end report: show average profit if we had bought and held for 5 years
* Better report visualization
* Auto-find best parameters for `rise_limit`, `sink_limit`, and `cool_off_span`
