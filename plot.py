#!/usr/bin/env python3

import matplotlib.pyplot as plt
import pickle
import sys
import numpy as np

data = pickle.load(open(sys.argv[1], "rb"))
plt.imshow(data)
plt.show()

