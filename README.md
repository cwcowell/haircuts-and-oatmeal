# Haircuts and Oatmeal

This is an **extremely simple** algorithmic trading program. It doesn't actually trade; it's just a tool for figuring out how well the world's most basic trading algorithm *would have* worked, using historical pricing data.

The name is a highly bastardized version of a concept from a Shel Silverstein poem, in which he claims "Daddy spends all his money on haircuts and oatmeal." I'm probably remembering that 98% wrong, but it's become a family meme around my house.


### To run
* install conda
* `cd <repo_root>`
* `conda env create -f environment.yml`
* `source activate HaircutsAndOatmeal` (on Windows use `activate HaircutsAndOatmeal` instead)
* `cd src`
* `python HaircutsAndOatmeal.py`


### To run tests
* `cd <repo_root>`
* `behave test/features`


### Author
Chris Cowell


### To Do
* Add Cucumber user acceptance tests
* Add unit tests
* Complete docstrings
* Add comparison data to end report: show average profit if we had bought and held for 5 years
* Better report visualization
* Auto-find best parameters for `rise_limit`, `sink_limit`, and `cool_off_span`
* Improve usage message in load_database.py


### Acknowledgments
The dataset is from https://www.kaggle.com/camnugent/sandp500, released under CC0 1.0 license.
