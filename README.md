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


### Acknowledgments
The dataset is from https://www.kaggle.com/camnugent/sandp500, released under CC0 1.0 license.


### To Do
Add the visualization code to the repo in a `Visualization.py` class.