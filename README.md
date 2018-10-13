# Haircuts and Oatmeal

This is an **extremely simple** algorithmic trading program. It doesn't actually trade; it's just a tool for figuring out how well the world's most basic trading algorithm *would have* worked, using historical pricing data.

The name is a highly bastardized version of a concept from a Shel Silverstein poem, in which he claims "Daddy spends all his money on haircuts and oatmeal." I'm probably remembering that 98% wrong, but it's become a family meme around my house.


### To run
* use `conda install` or another Python environment management tool to install dependencies
    * numpy
    * pandas
    * python 3.6 or higher
    * sqlite3
    * termcolor
* `cd <repo_root>/src`
* `python HaircutsAndOatmeal.py`


### To run tests
* install `behave` module
* `cd <repo_root>`
* `behave test/features`


### Author
Chris Cowell


### To Do
* Better report visualization
* Auto-find best parameters for `rise_limit`, `sink_limit`, and `cool_off_span`
* How does it compare to actual buy & hold rate of return:
    - closed at 267.67 on Feb 7, 2018
    - closed at 151.80 on Feb 8, 2013
    - diff is 115.87
    - 115.87 / 151.80 = 76%    
* Note that this algorithm ignores dividends

### Acknowledgments
The dataset is from https://www.kaggle.com/camnugent/sandp500, released under CC0 1.0 license.
