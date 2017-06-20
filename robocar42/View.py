import os
import time
import thread

import cv2
import numpy as np

class View(object):
    '''
    Image object class. Handles displaying and saving the images.
    '''
    def __init__(self, show_only=True):
        self.show_only = show_only

    def save(self, images):
        