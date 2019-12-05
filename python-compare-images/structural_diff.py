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
import multiprocessing
import sys

def mse(imageA, imageB):
  err = np.sum((imageA - imageB) ** 2)
  err /= float(imageA.shape[0] * imageA.shape[1])
  return err


def structural_sim(jpeg_path, tif_images):
  jpegs_path, jpeg_fname = jpeg_path
  jpeg = common.get_imgEx(jpegs_path, jpeg_fname)[-1]
  best = None
  for tifs_path, tif_fname, tif in tifs:
    m = mse(jpeg, tif)
    #print(jpeg_fname, tif_fname, m)
    if best == None:
      best = (tif_fname, m)
    else:
      best = min(best, (tif_fname, m), key=lambda x: x[1])
  return (jpeg_fname, *best)


if __name__ == '__main__':
  print(datetime.datetime.now().time())
  tifs_path = "../ALL TIF REDUCED"
  jpegs_path = "../ALL JPG REDUCED"
  #tifs_path = "../Samples/TIF REDUCED"
  #jpegs_path = "../Samples/JPG REDUCED"

  print("loading images")
  tifs, jpegs = [], []
  with multiprocessing.Pool(processes=4) as pool:
    tifs = pool.starmap(common.get_imgEx, [(tifs_path, f) for f in os.listdir(tifs_path)])
  print("loaded images")

  with multiprocessing.Pool(processes=4) as pool:
    results = pool.starmap(structural_sim, [((jpegs_path, jpeg_fname), tifs) for jpeg_fname in os.listdir(jpegs_path)])
  with open("results-sim.csv", "w") as out:
    writer = csv.writer(out)
    for r in results:
      writer.writerow(r)
  
  print(datetime.datetime.now().time())