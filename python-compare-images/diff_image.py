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

warnings.filterwarnings('ignore')


# specify resized image sizes
height = 1000
width = 1000

def get_img(path, norm_size=True, norm_exposure=False):
  img = imread(path, flatten=True).astype(int)
  if norm_size:
    img = resize(img, (height, width), anti_aliasing=True, preserve_range=True)
  if norm_exposure:
    img = normalize_exposure(img)
  return img


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


def earth_movers_distance(img_a, img_b):
  hist_a = get_histogram(img_a)
  hist_b = get_histogram(img_b)
  return wasserstein_distance(hist_a, hist_b)


def structural_sim(path_a, path_b):
  img_a = get_img(path_a)
  img_b = get_img(path_b)
  sim, diff = compare_ssim(img_a, img_b, full=True)
  return sim


def pixel_sim(path_a, path_b):
  img_a = get_img(path_a, norm_exposure=True)
  img_b = get_img(path_b, norm_exposure=True)
  return np.sum(np.absolute(img_a - img_b)) / (height*width) / 255


def sift_sim(path_a, path_b):
  # initialize the sift feature detector
  orb = cv2.ORB_create()

  # get the images
  img_a = cv2.imread(path_a)
  img_b = cv2.imread(path_b)

  # find the keypoints and descriptors with SIFT
  kp_a, desc_a = orb.detectAndCompute(img_a, None)
  kp_b, desc_b = orb.detectAndCompute(img_b, None)

  # initialize the bruteforce matcher
  bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

  # match.distance is a float between {0:100} - lower means more similar
  matches = bf.match(desc_a, desc_b)
  similar_regions = [i for i in matches if i.distance < 70]
  if len(matches) == 0:
    return 0
  return len(similar_regions) / len(matches)

def get_hist(f, path):
  print(f)
  return (f, get_histogram(get_img(os.path.join(path, f), norm_exposure=True)))


if __name__ == '__main__':

  tifs_path = "../ALL TIF REDUCED"
  jpegs_path = "../ALL JPG REDUCED"
  #tifs_path = "../Samples/TIF"
  #jpegs_path = "../Samples/JPG"

  print("loading images")
  tifs = []
  with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    futures_tifs = [executor.submit(get_hist, f, tifs_path) for f in os.listdir(tifs_path)]
    futures_jpegs = [executor.submit(get_hist, f, jpegs_path) for f in os.listdir(jpegs_path)]
    jpegs = [f.result() for f in futures_jpegs]
    tifs = [f.result() for f in futures_tifs]

  try:
    f1 = open("results_clean-{}.csv".format(datetime.datetime.now().time()), "a")
    f2 = open("results_clash-{}.csv".format(datetime.datetime.now().time()), "a")
    print("loaded images")
    results = []
    k = 0
    for jpeg_filename, jpeg_histogram in jpegs:
      matches = []
      for tif_filename, tif_histogram in tifs:
        emd = wasserstein_distance(tif_histogram, jpeg_histogram)
        matches.append((jpeg_filename, emd))
      #print(min(matches, key=lambda m: m[1]))
      results.append((jpeg_filename, *min(matches ,key=lambda m: m[1])))
      f1.write("{},{},{}\n".format(*results[-1])
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
      else:
        f1.write("{},{},{}\n".format(*x))
  finally:
    f1.close()
    f2.close()