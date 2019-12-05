import os
import sys


bad_imgs = [l.strip() for l in open(sys.argv[2]).readlines()]
lines = [l.strip().replace('"', '') for l in open(sys.argv[1]).readlines()]
result = [l for l in lines if l.split(',')[0].strip() not in bad_imgs]
print('\n'.join(result))
