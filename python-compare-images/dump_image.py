import sys
import os
import numpy as np
from scipy import misc
import matplotlib.pyplot as plt

if len(sys.argv) < 2:
    print("bad usage")
    sys.exit(1)

photo_data = misc.imread(sys.argv[1])
with open(os.path.basename(sys.argv[1])+"-dump.txt", "w") as f:
    data = []
    for x in photo_data:
        for y in x:
            if sys.argv[1].endswith("tif"):
                data.append(y)
            else:
                data.append((int(y[0])+int(y[1])+int(y[2]))//3)
    data = [str(x) for x in data]
    s = ' '.join(data)
    f.write(s)

