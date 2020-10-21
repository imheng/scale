import os
import sys

folder = sys.argv[1]
print('Input: ',folder)

for f in os.listdir(folder):
    print(f)
