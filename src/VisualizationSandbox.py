import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df = pd.read_csv('data/results-good.csv', skipfooter=1, engine='python')

x = df['RISE LIMIT']
y = df['GRAND PERCENT CHANGE']
fix, ax = plt.subplots()
ax.scatter(x, y)
plt.show()

# x = np.array([0, 1, 2, 3, 5, 10, 15, 16, 17, 18, 19, 20, 30])
# y = np.sin(x)

