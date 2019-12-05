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
import threading


warnings.filterwarnings('ignore')

def get_img(path, norm_exposure=False):
  img = imread(path, flatten=True).astype(float)
  if norm_exposure:
    img = normalize_exposure(img)
  return img

def get_imgEx(path, fname):
  return (path, fname, get_img(os.path.join(path, fname), norm_exposure=True))

def get_histNorm(path, fname):
    return (path, fname, get_histogram(get_img(os.path.join(path, fname), norm_exposure=True)))


def get_histogram(img):
  h, w = img.shape
  hist = [0.0] * 256
  for i in range(h):
    for j in range(w):
      hist[img[i, j]] += 1
  return np.array(hist) / (h * w) 

def normalize_exposure(img, hist=None):
  img = img.astype(int)
  if hist == None:
    hist = get_histogram(img)
  cdf = np.array([sum(hist[:i+1]) for i in range(len(hist))])
  sk = np.uint8(255 * cdf)
  height, width = img.shape
  normalized = np.zeros_like(img)
  for i in range(0, height):
    for j in range(0, width):
      normalized[i, j] = sk[img[i, j]]
  return normalized.astype(int)

