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



warnings.filterwarnings('ignore')


def get_img(path, norm_size=True, norm_exposure=False):
  img = imread(path, flatten=True).astype(float)
  if norm_exposure:
    img = normalize_exposure(img)
  return img

def get_histNorm(path, fname):
    return (path, fname, get_histogram(get_img(os.path.join(path, fname), norm_exposure=True)))

def get_histogram(img):
  h, w = img.shape
  hist = [0.0] * 256
  for i in range(h):
    for j in range(w):
      hist[img[i, j]] += 1
  return np.array(hist) / (h * w) 


def normalize_exposure(img):
  '''
  Normalize the exposure of an image.
  '''
  img = img.astype(int)
  hist = get_histogram(img)
  # get the sum of vals accumulated by each position in hist
  cdf = np.array([sum(hist[:i+1]) for i in range(len(hist))])
  # determine the normalization values for each unit of the cdf
  sk = np.uint8(255 * cdf)
  # normalize each position in the output image
  height, width = img.shape
  normalized = np.zeros_like(img)
  for i in range(0, height):
    for j in range(0, width):
      normalized[i, j] = sk[img[i, j]]
  return normalized.astype(int)




if __name__ == '__main__':

  #tifs_path = "../ALL TIF REDUCED"
  #jpegs_path = "../ALL JPG REDUCED"
  tifs_path = "../Samples/TIF REDUCED"
  jpegs_path = "../Samples/JPG REDUCED"

  print("loading images")
  tifs, jpegs = [], []
  with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    futures_tifs = [executor.submit(get_imgEx, tifs_path, f) for f in os.listdir(tifs_path)]
    futures_jpegs = [executor.submit(get_imgEx, jpegs_path, f)  for f in os.listdir(jpegs_path)]
    jpegs = [f.result() for f in futures_jpegs]
    tifs = [f.result() for f in futures_tifs]
  print("loaded images")
  
  with open("results-sim.csv", "w") as out:
    writer = csv.writer(out)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
      futures = [executor.submit(structural_sim, jpeg, tifs) for jpeg in jpegs]
      executor.shutdown()
