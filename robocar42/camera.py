import os
import time
import subprocess as sp
from threading import Thread

import cv2
import numpy as np

import config

class Camera(object):
    '''
    Camera object class.
    '''
    def __init__(self, name, conf, res=(320,240), log=False):
        self.name = name
        log_name = '%s/%s.log' % (config.log_path, self.name)
        if log:
            self._stderr = open(log_name, 'w')
        else:
            self._stderr = open('/dev/null', 'w')
        _r, _w = os.pipe()
        self._r = os.fdopen(_r)
        self._w = os.fdopen(_w, 'w')
        self.shape = (res[0], res[1], 3)
        self.image = None
        self.stopped = False

        #setting up camera
        input_url = ("%s://%s:%s@%s/%s" % (
                conf['cam_protocol'],
                conf['cam_user'],
                conf['cam_pass'],
                conf['cam_url'],
                conf['cam_channel']
            )
        )
        ffmpeg_cmd = [
            'ffmpeg',
            '-i', input_url,
            '-vf', 'fps=15',
            '-f', 'image2pipe',
            '-pix_fmt', 'rgb24',
            '-vcodec', 'rawvideo',
            'pipe:1'
        ]
        self.ffmpeg = sp.Popen(
            ffmpeg_cmd,
            stdout=self._w,
            stderr=self._stderr,
            bufsize=10**8
        )
        time.sleep(3)
        self.recording = True
        self.start()

    def start(self):
        t = Thread(target=self.update)
        t.daemon = True
        t.start()
        time.sleep(1)
        return self

    def stop(self):
        self._w.close()
        self._stderr.close()
        if self.ffmpeg:
            self.ffmpeg.kill()
        self.recording = False

    def update(self):
        '''
        Captures the current frame of the camera and return the image file
        '''
        while True:
            raw_image = self._r.read(
                self.shape[0]
                * self.shape[1]
                * self.shape[2]
            )
            image = np.fromstring(raw_image, dtype='uint8')
            image = image.reshape((res[1], res[0], res[3]))
            image = np.swapaxes(image, 0, 1)
            self.image = image
            if not self.recording:
                self._r.close()
                self.stopped = True
                break