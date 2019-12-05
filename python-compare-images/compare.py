from skimage.measure import _structural_similarity as ssim
import matplotlib.pyplot as plt
import numpy as np
import cv2
import os
import sys

def mse(imageA, imageB):
	err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
	err /= float(imageA.shape[0] * imageA.shape[1])
	
	return err

def compare_images(imageA, imageB, title):
	print(imageA.shape, imageB.shape)
	hA, wA = imageA.shape
	hB, wB = imageB.shape
	if hA > hB or wA > wB:
		imageA = cv2.resize(imageA, (wB, hB))
	elif hB > hA or wB > wA:
		imageB = cv2.resize(imageB, (wA, hA))
	m = mse(imageA, imageB)
	s = ssim.compare_ssim(imageA, imageB)
	return s


images_path = "../Samples"

tifs_filename = [f for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f)) and f.endswith(".tif")]
jpegs_filename = [f for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f)) and f.endswith(".jpg")]
for tif_filename in tifs_filename:
	tif = cv2.imread(os.path.join(images_path, tif_filename))
	tif = cv2.cvtColor(tif, cv2.COLOR_BGR2GRAY)

	jpegs = [None] * len(jpegs_filename)
	for i in xrange(len(jpegs)):
		jpegs[i] = cv2.imread(os.path.join(images_path, jpegs_filename[i]))
		jpegs[i] = cv2.cvtColor(jpegs[i], cv2.COLOR_BGR2GRAY)

	matches = []
	print(tif_filename)
	for i in range(len(jpegs)):
		m = compare_images(tif, jpegs[i], jpegs_filename[i])
		matches.append((m, jpegs_filename[i]))
	
	matches.sort(reverse=True)
	print(matches[0])