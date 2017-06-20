import os
import time
import logging
from threading import Thread

import config
from car import Car
from train import model, prediction

class CoreControl(object):
    '''
    Core Control object class.
    '''
    def __init__(self, csv_file, header):
        self.header = header
        self.data = []
        self.csv_file = csv_file

    def record_data(self, new_data):
        if len(new_data) != len(header):
            return
        new_entry = dict(zip(self.header, new_data))
        data.append(new_entry)

    def send_control(self, car, req):
        if not car.drive(req):
            return False
        return True

class ManualControl(CoreControl):
    '''
    Manual Control object class.
    Extreme range motions
    ''' 
    def __init__(self, csv_file, header):
        self.header = header
        self.data = []
        self.csv_file = csv_file

class ManualControlPrec(CoreControl):
    '''
    Manual Control Precision object class.
    Variable angle motions
    '''
    def __init__(self, csv_file, header):
        pass

class AutoControl(CoreControl):
    '''
    Auto Control object class.
    Extreme range motions
    '''
    def __init__(self, csv_file, header):
        pass

class AutoControlPrec(CoreControl):
    '''
    Auto Control object class.
    Variable angle motions
    '''
    def __init__(self, csv_file, header):
        pass