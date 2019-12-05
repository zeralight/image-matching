import warnings
from skimage.measure import compare_ssim
from skimage.transform import resize
from scipy.stats import wasserstein_distance
from scipy.misc import imsave
from scipy.ndimage import imread
import numpy as np
import cv2
import os
import datetime
import concurrent.futures
import csv
import common
import threading

"""
def earth_movers_distance(img_a, img_b):
    hist_a = common.get_histogram(img_a)
    hist_b = common.get_histogram(img_b)
    return wasserstein_distance(hist_a, hist_b)

def row_to_object(p, f, h):
    return (p, f, np.array([float(x) for x in h.split(' ')]))

if __name__ == '__main__':
    tifs = []
    jpegs = []
    with open("histo.csv") as histo_file:
        reader = csv.reader(histo_file, delimiter=",")
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            future_tifs, future_jpegs = [], []
            for t, p, f, h in reader:
                if t == "tif":
                    future_tifs.append(executor.submit(row_to_object, p, f, h))
                else:
                    future_jpegs.append(executor.submit(row_to_object, p, f, h))
        tifs = [f.result() for f in future_tifs]
        jpegs = [f.result() for f in future_jpegs]
        
    f1 = open("results_clean-histo.csv", "a")
    f2 = open("results_clash-histo.csv", "a")
        
    results = []
    k = 0
    for jpegs_path, jpeg_filename, jpeg_histogram in jpegs:
        best = None
        for tifs_path, tif_filename, tif_histogram in tifs:
            emd = wasserstein_distance(tif_histogram, jpeg_histogram)
            if best == None:
                best = (tif_filename, emd)
            else:
                best = min((best, (tif_filename, emd)), key=lambda m: m[1])
        results.append((jpeg_filename, *best))
        f1.write("{},{},{}\n".format(*results[-1]))
        k += 1
        if k%10 == 0:
            print(datetime.datetime.now().time(), ":", k)

    clashes = set()
    for i in range(len(results)):
        for j in range(i+1, len(results)):
            if results[i][1] == results[j][1]:
                clashes.add(results[i][0])
                clashes.add(results[j][0])
    for x in results:
        if tif_filename in clashes:
            f2.write("{},{},{}\n".format(*x))
    f1.close()
    f2.close()
"""

def earth_moveers_distance(jpeg_path, tifs):
  jpegs_path, jpeg_fname = jpeg_path
  jpegs_path, jpeg_fname, jpeg_hist = common.get_histNorm(jpegs_path, jpeg_fname)
  #print(jpegs_path, jpeg_fname, jpeg_hist, sep=' | ')
  best = None
  for (tifs_path, tif_fname, tif_hist) in tifs:
    m = wasserstein_distance(jpeg_hist, tif_hist)
    #print(jpeg_fname, tif_fname, m)
    if best == None:
      best = (tif_fname, m)
    else:
      best = min(best, (tif_fname, m), key=lambda x: x[1])
  with lock:
    writer.writerow((jpeg_fname, *best))

if __name__ == '__main__':
  lock = threading.Lock()

  #tifs_path = "../ALL TIF REDUCED"
  #jpegs_path = "../ALL JPG REDUCED"
  tifs_path = "../Samples/TIF REDUCED"
  jpegs_path = "../Samples/JPG REDUCED"

  print("loading images")
  tifs, jpegs = [], []
  with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    futures_tifs = [executor.submit(common.get_histNorm, tifs_path, f) for f in os.listdir(tifs_path)]
    tifs = [f.result() for f in futures_tifs]
  print("loaded images")
  
  with open("results-emd.csv", "w") as out:
    writer = csv.writer(out)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
      futures = [executor.submit(earth_moveers_distance, (jpegs_path, jpeg_fname), tifs) for jpeg_fname in os.listdir(jpegs_path)]
      executor.shutdown()
