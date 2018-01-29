#!/usr/bin/env python

'''
plots image as logPolar and linearPolar

Usage:
    logpolar.py

Keys:
    ESC    - exit
'''

# Python 2/3 compatibility
from __future__ import print_function

import cv2

if __name__ == '__main__':
    print(__doc__)

    import sys
    try:
        fn = sys.argv[1]
    except IndexError:
        #fn = '../data/fruits.jpg'
        fn = '../data/space_background.jpg'

    img = cv2.imread(fn)
    if img is None:
        print('Failed to load image file:', fn)
        sys.exit(1)

    #img2 = cv2.logPolar(img, (img.shape[0]/2, img.shape[1]/2), 40, cv2.WARP_FILL_OUTLIERS)
    iter_range=10
    import time
    start_ts=time.time()
    for iter in range(iter_range):
        img3 = cv2.linearPolar(img, (img.shape[0]/2, img.shape[1]/2), 320, cv2.WARP_FILL_OUTLIERS)
    print("fps: "+str(iter_range/(time.time()-start_ts)))
	
    cv2.imwrite('../data/zz_test.jpg',img3)
	
    #cv2.imshow('before', img)
    #cv2.imshow('logpolar', img2)
    cv2.imshow('linearpolar', img3)

    cv2.waitKey(0)
