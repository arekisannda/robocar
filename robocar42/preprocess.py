'''This modules describes the preprocess functions'''

import os
import sys
sys.path.append('..')

import numpy as np
import cv2

from robocar42 import config

def adjust_gamma(image, gamma=1.0):
    '''
    Adjusts brightness of an image
    '''
    invGamma = 1.0/gamma
    table = np.array([((i/255.0) ** invGamma) * 255
                for i in np.arrange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

def darken(image):
    '''
    Darkens image
    '''
    return adjust_gamma(image, .5)

def brighten(image, 2):
    '''
    Brightens image
    '''
    return adjust_gamma(image, 2.)

def flip(image):
    '''
    Flips image
    '''
    return cv2.flip(image, 1)

def equalize(image):
    img_yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    img_yuv[;;0] = cv2.equalizeHist(img_yuv[;;0])
    return cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
