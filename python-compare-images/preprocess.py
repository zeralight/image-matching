from os.path import join, isfile
from os import remove
import csv
import datetime
import concurrent.futures
import sys


# Remove found files
if __name__ == '__main__':

  tifs_path = "../ALL_TIF"
  jpegs_path = "../ALL_JPG"

  not_found_jpegs, not_found_tifs = 0, 0
  k = 0
  with open(sys.argv[1], "r") as f:
      reader = csv.reader(f, delimiter=",")
      next(reader, None)
      for row in reader:
          row[0] = row[0].replace('"', '')
          row[1] = row[1].replace('"', '')
          if isfile(join(tifs_path, row[0])):
              remove(join(tifs_path, row[0]))
          else:
              not_found_tifs += 1
          if isfile(join(jpegs_path, row[1])):
              remove(join(jpegs_path, row[1]))
          else:
              not_found_jpegs += 1
      k += 1
      if k%1000 == 0: print(k)
  print("not_found jpegs: {}\nnot_found tifs: {}".format(not_found_jpegs, not_found_tifs))