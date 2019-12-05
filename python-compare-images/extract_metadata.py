from multiprocessing import Pool
import os
import sys
import subprocess
import re

jpgs_dir='../ALL_JPG'
tifs_dir='../ALL_TIF'

def f(lines, chunk):
    result = []
    for i in chunk:
        line = lines[i]
        result.append(subprocess.check_output(["./extract_metadata.sh", line]))
    return str(b'\n'.join(result), "utf8")
    
if __name__ == "__main__":
    lines = [line.strip() for line in open(sys.argv[1]).readlines()]
    #print(len(lines))
    blocks = [( range(i*(len(lines)//6), (i+1)*(len(lines)//6)) ) for i in range(5)]
    blocks.append(range(blocks[-1][1], len(lines)))
    #print(blocks)
    with Pool(processes=6) as pool:
        futures = pool.starmap(f, [(lines, chunk) for chunk in blocks])
    text = '\n'.join(futures)
    print("\"TIF File Name\",\"JPG File Name\",\"Title\",\"Description\",\"Subject\",\"Caption-Abstract\",\"Keywords\"")
    print(re.sub(r"\n+", "\n", text)[:-1:])