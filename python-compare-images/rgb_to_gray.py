from PIL import Image
import os
import re
import datetime
import concurrent.futures
import cv2
import sys

n = int(sys.argv[1])
height, width = n, n

def convert_file(path, f, out_path):
    in_f = os.path.join(path, f)
    out_f = os.path.join(out_path, re.sub(r"tif$", "jpg", f))
    cv2.imwrite(out_f, cv2.cvtColor(cv2.resize(cv2.imread(in_f), (width, height)), cv2.COLOR_BGR2GRAY))
    #cv2.imwrite(out_f, cv2.cvtColor(cv2.imread(in_f), cv2.COLOR_BGR2GRAY))
    

if __name__ == "__main__":
    print(datetime.datetime.now().time())
    for path in ("../ALL_JPG", "../ALL_TIF"):
    #for path in ("../Samples/JPG", "../Samples/TIF"):
        out_path = path + "_REDUCED_" + str(height)
        os.makedirs(out_path, exist_ok=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures_results = [executor.submit(convert_file, path, f, out_path) for f in os.listdir(path)]
            executor.shutdown()
    print(datetime.datetime.now().time())

