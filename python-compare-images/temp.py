import os
import sys


bad_imgs = [l.strip() for l in open(sys.argv[2]).readlines()]
lines = [l.strip().replace('"', '') for l in open(sys.argv[1]).readlines()]
result = [l.split('\t') for l in lines if l.split('\t')[1].strip() not in bad_imgs]
result = [l[1]+','+l[0] for l in result]
print('\n'.join(result))
