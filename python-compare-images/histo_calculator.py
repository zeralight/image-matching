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
import common
import threading
import csv

def set_hist(type_, path, f):
  print(type_, path, f)
  hist = common.get_histogram(common.get_img(os.path.join(path, f), norm_exposure=True))
  with lock:
    writer.writerow([type_, path, f, ' '.join(str(x) for x in hist)])


if __name__ == '__main__':
  lock = threading.Lock()

  #tifs_path = "../ALL TIF REDUCED"
  #jpegs_path = "../ALL JPG REDUCED"
  tifs_path = "../Samples/TIF REDUCED"
  jpegs_path = "../Samples/JPG REDUCED"

  print("loading images")
  with open("histo.csv", "w") as f:
    writer = csv.writer(f, delimiter=",")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
      futures = {executor.submit(set_hist, type_, path, fname) for (type_, path) in (("jpg", jpegs_path), ("tif", tifs_path)) for fname in os.listdir(path)}
      executor.shutdown()