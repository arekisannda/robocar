'''
Drive entry point
'''

import sys
import os
from os.path import dirname
from os.path import basename
import time
import argparse
import atexit
import signal
import logging
sys.path.append(dirname(dirname(os.path.realpath(__file__))))

import cv2
import numpy as np
import pygame
import pyping

from robocar42 import config, util, models
from robocar42.car import Car
from robocar42.display import Display

logger = util.configure_log('drive')

NUM_CLASSES = 4
delta_time = 1000
conf_level = 0.3

rc_car = Car(config.vehicle_parser_config('vehicle.ini'))
disp_conf = config.display_parser_config('display.ini')
cam_1 = config.camera_parser_config('camera_1.ini')
cam_2 = config.camera_parser_config('camera_2.ini')
model_conf = config.model_parser_config('model_1.ini')

links = ['/fwd', '/fwd/lf', '/fwd/rt', '/rev', '/rev/lf', '/rev/rt', '']
rev_action = 3

def check_cameras():
    try:
        cam_1_ret = pyping.ping(cam_1['cam_url'], udp=True).ret_code
        cam_2_ret = pyping.ping(cam_2['cam_url'], udp=True).ret_code
        if not cam_1_ret and not cam_2_ret:
            return True
    except:
        pass
    return False

def ctrl_c_handler(signum, frame):
    pygame.quit()
    exit(0)

def cleanup(display):
    display.stop()
    exit(0)

def conv_to_vec(action):
    '''
    Convert old car actions into vect for car module
    '''
    req = [0] * 4
    if '/fwd' in action: req[0] = 1
    elif '/rev' in action: req[0] = -1
    else: req[0] = 0
    req[1] = rc_car.max_speed
    if '/lf' in action: req[2] = -1
    elif '/rt' in action: req[2] = 1
    else: req[2] = 0
    req[3] = -1
    print req
    return req

def process_image(images):
    '''
    Processes images and return normalized/combined single image
    '''
    images[0] = np.swapaxes(images[0], 1, 0)
    images[1] = np.swapaxes(images[1], 1, 0)
    aimage = np.concatenate(tuple(images), axis=1)
    aimage = cv2.resize(aimage,
                disp_conf['sdshape'],
                interpolation=cv2.INTER_AREA)
    aimage = aimage / 255.
    aimage = aimage - 0.5
    return aimage

def auto_drive(images):
    print "auto drive func"
    if images:
        prec_image = process_image(images)
        pred_act = model.predict(np.array([prec_image]))[0]
        logger.info("Lft: %.2f | Fwd: %.2f | Rht: %.2f | Rev: %.2f" %
            (pred_act[1], pred_act[0], pred_act[2], pred_act[3]))
        act_i = np.argmax(pred_act)
        action = act_i if (pred_act[act_i] >= conf_level) else rev_action
        if act_i < len(links):
            rc_car.drive(conv_to_vec(links[act_i]))
    else:
        logger.error("Error: no images for prediction")
    return None, None

def drive(auto):
    ot = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        ct = time.time()
        drive = True if (ct - ot) * 1000 > rc_car.exp + delta_time else drive
        surface, images, filenames = disp.show()
        screen.blit(surface[0], (0,0))
        screen.blit(surface[1], (disp_conf['oshape'][0],0))
        pygame.display.flip()
        if images and auto and drive:
            logger.debug("Auto drive")
            drive = False
            pred_act, act_i = auto_drive(images)
            ot = ct

if __name__ == '__main__':
    signal.signal(signal.SIGINT, ctrl_c_handler)
    if check_cameras():
        model = models.model(True, model_conf['shape'],
                    NUM_CLASSES,
                    'models/june_16_2pm.h5')
        rc_car.start()
        disp = Display('main', disp_conf, ['camera_1.ini', 'camera_2.ini'])
        atexit.register(cleanup, disp)
        pygame.init()
        screen = pygame.display.set_mode(disp_conf['doshape'])

        drive(True)
        disp.stop()
        pygame.quit()
    else:
        logger.error("Error: Unable to reach cameras!\nPlease make sure to check if the car is on and batteries are fully charged.\nTry again.")
	exit(0)
