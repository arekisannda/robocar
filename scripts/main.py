'''
This script is the main entry point of the project.
'''

import sys
import os
from os.path import dirname
from os.path import basename
import time
import signal
import argparse
import atexit
sys.path.append(dirname(dirname(os.path.realpath(__file__))))

import pygame
import numpy as np
import pandas as pd

from robocar42.display import display
from robocar42.car import Car
from robocar42 import config
from robocar42 import models

actions = [pygame.K_UP,pygame.K_LEFT,pygame.K_RIGHT,pygame.K_DOWN]

def build_parser():
    '''
    Build parser
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-config',
        type=str,
        default='',
        help='Name of drive configuration file to use. Default: set_1.ini'
    )
    parser.add_argument(
        '-auto',
        action='store_true',
        default=False,
        help='Sets autopilot mode on/off. Default: off'
    )
    parser.add_argument(
        '-train',
        type=str,
        default='',
        help='Sets train mode on/off and names the training set. Default: \'\''
    )
    parser.add_argument(
        '-model',
        type=str,
        default='',
        help='Name of model h5 file'
    )
    return parser

def verify_args(args):
    '''
    Verifies the passed in command line arguments
    '''
    if args.config:
        drive_conf = config.drive_parser_config(args.config)
    else:
        drive_conf = config.drive_parser_config('set_1.ini')

    if args.train:
        rec_folder = os.path.join(config.stream_path, args.train)
        rec_dirs = [rec_foldre+'/'+str(i+1) for i in range(2)]
        for directory in rec_dirs:
            if not os.path.exists(directory):
                os.makedirs(directory)
    else:
        rec_dirs = None

    if args.model:
        model_path = os.path.join(config.model_path, args.model)
        if not os.path.exists(model_path):
            print "Model does not exist."
            exit(0)
    else:
        model_path = None

    return drive_conf, rec_dirs, model_path

def display_frames(surfaces):
    screen.blit(surfaces[0], (0,0))
    screen.blit(surfaces[1], (disp_conf['oshape'][0], 0))
    pygame.display.flip()

def record_data(action, filenames):
    global records
    entry = filenames
    entry.append(action)
    records.append(entry)

def manual_drive(filenames, intent, teach):
    action = [
        [1, rc_car.max_speed, 0, rc_car.straight],
        [1, rc_car.max_speed, -1, rc_car.left],
        [1, rc_car.max_speed, 1, rc_car.right],
        [-1, rc_car.max_speed, 0, rc_car.straight],
        [-1, rc_car.max_speed, -1, rc_car.left],
        [-1, rc_car.max_speed, 1, rc_car.right]]

    for act_i in range(len(actions)):
        tmp = actions[act_i]
        if tmp == intent:
            try:
                if not teach:
                    rc_car.drive(action[act_i])
                if train and act_i < 6:
                    record_data(act_i, filenames)
            except:
                pass
            return

def drive(auto, teach, rec_dirs, model):
    intent = 0
    ot = 0
    train = True if rec_dirs else False

    while True:
        surfaces, images, filenames = disp.show(train, rec_dirs)
        display_frames(surfaces)

        ct = time.time()
        drive = True if (ct-ot) * 1000 > delay_time + exp_time else drive
        keys = pygame.key.get_pressed()
        for act_i in range(len(actions)):
            tmp = actions[act_i]
            if keys[tmp]:
                intent = tmp
        if (keys[pygame.K_ESCAPE] or keys[pygame.K_q] or
            pygame.event.peek(pygame.QUIT)):
            return
        if drive and not auto:
            drive = False
            manual_drive(filenames, intent, teach)
            ot = ct
        if keys[pygame.K_a]:
            auto = True
        if keys[pygame.K_s]:
            auto = False
        keys = []
        pygame.event.pymp()

        if auto and drive and images:
            drive = False
            auto_drive(images)
            ot = ct

def ctrl_c_handler(signum, frame):
    '''
    Handles signal interrupts to allows for clean exit.
    '''
    pygame.quit()
    exit(0)

def cleanup(display):
    display.stop()
    if records:
        column = ['cam_1', 'cam_2', 'action']
        df = pd.DataFrame(records, columns=column)
        label_path = os.path.join(config.label_path, args.train+".csv")
        df.to_csv(label_path, index=False)
    exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, ctrl_c_handler)
    parser = build_parser()
    args = parser.parser_args()
    drive_conf, rec_dirs, model_path = verify_args(args)

    disp_conf = config.display_parser_config(drive_conf['display'])
    car_conf = config.vehicle_parser_config(drive_conf['vehicle'])
    rc_car = Car(car_conf)
    disp = Display('main', disp_conf, drive_conf['camera'])

    car_speed = car_conf['speed']
    exp_time = car_conf['exp']
    delay_time = drive_conf['delay']
    conf_level = drive_conf['level']
    num_classes = drive_conf['classes']
    teach = drive_conf['teach']

    records = []
    atexit.register(cleanup, display)

    pygame.init()
    screen = pygame.display.set_mode(disp_conf['doshape'])
    records = drive(
        auto=args.auto,
        rec_dirs=rec_dirs,
        model_path=model_path)
    display.stop()
    pygame.quit()
