'''
This modules processes a data set and increases it by labeling inbetween
frames. It also zips the processed data set and pushes it onto the 
cloud storage instance.
'''

import sys
import os
from os.path import dirname
from os.path import basename
import time
import argparse
import zipfile
from datetime import datetime
from collections import deque
import logging
sys.path.append(dirname(dirname(os.path.realpath(__file__))))

import numpy as np
import pandas as pd
from google.cloud import storage

from robocar42.util import progress_bar
from robocar42 import config

logger = logging.getLogger(__name__)

def build_parser():
    '''
    Build Parser
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-log',
        type=str,
        default='INFO',
        help='Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL'
    )
    parser.add_argument(
        '-push',
        action='store_true',
        default=False,
        help='Enable pushing zip to bucket. Default: False'
    )
    parser.add_argument(
        'set_name',
        type=str,
        help="Name of data set"
    )
    return parser

def configure_log(loglevel, set_name):
    '''
    Configures the logging message settings
    '''
    global logger
    log_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(log_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    log_file = os.path.join(
        config.log_path,
        time.strftime("%d_%m_%Y_%H_%M_")+set_name+'.log'
    )

    fh = logging.FileHandler(log_file, mode='w')
    fh.setLevel(logging.DEBUG)
    fh_formatter = logging.Formatter('%(asctime)s - %(message)s')
    fh.setFormatter(fh_formatter)

    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    ch_formatter = logging.Formatter('%(message)s')
    ch.setFormatter(ch_formatter)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    logger.addHandler(ch)

def get_ctime(path, filename):
    '''
    Gets the creation time of a file
    '''
    tmp = os.path.join(path, filename)
    stat_info =  os.stat(tmp)
    ts = stat_info.st_mtime
    st = datetime.fromtimestamp(ts).strftime('%Y%m%d-%H%M%S-%f')[:-4]
    return st

def push_to_cloud(set_name, zip_file):
    '''
    Pushes zip data set onto the cloud
    '''
    zip_bname = basename(zip_file)
    logger.critical("-----push_to_cloud start-----")
    cloud_conf = config.cloud_parser_config('cloud.ini')
    client = storage.Client()
    bucket = client.get_bucket(cloud_conf['bucket'])
    blob_name = os.path.join(cloud_conf['folder'], zip_bname)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(zip_file)
    logger.critical("-----push_to_cloud end----")

def write_to_zip(set_name, zip_info):
    '''
    Writes the increased data set into a zip file
    '''
    zip_name = os.path.join(config.data_path, set_name+'.zip')
    entries, cam_1_path, cam_2_path = zip_info

    zp = zipfile.ZipFile(zip_name, mode='w')
    logger.critical("-----Creating zip file %s-----" % (zip_name))
    try:
        cam_1_bname = os.path.relpath(cam_1_path, config.pre_path)
        cam_2_bname = os.path.relpath(cam_2_path, config.pre_path)
        cnt = 0
        progress_bar(cnt, len(entries))
        for entry in entries:
            file_1 = os.path.join(cam_1_path, entry['cam_1'])
            zp.write(
                file_1,
                cam_1_bname+'/'+entry['cam_1'],
                zipfile.ZIP_DEFLATED
            )
            file_2 = os.path.join(cam_2_path, entry['cam_2'])
            zp.write(
                file_2,
                cam_2_bname+'/'+entry['cam_2'],
                zipfile.ZIP_DEFLATED
            )
            logger.debug('DEBUG - Zipped Files: %s, %s' %(
                entry['cam_1'],
                entry['cam_2'])
            )
            cnt += 1
            progress_bar(cnt, len(entries))
        df = pd.DataFrame(entries,
            columns=['timestamp',
                     'cam_1',
                     'cam_2',
                     'action']
        ) 
        sLength = len(df['timestamp'])
        array = np.asarray([set_name for s in range(sLength)])
        name_df = pd.Series(array)
        df.insert(0, 'setname', name_df)

        csv_file = set_name+'.csv'
        zp_csv_name = os.path.join(set_name, csv_file)
        csv_file = os.path.join(config.pre_path, zp_csv_name)
        df.to_csv(csv_file, index=False)
        zp.write(csv_file, zp_csv_name)

        meta_file = set_name+'.meta'
        zp_meta_name = os.path.join(set_name, meta_file)
        meta_file = os.path.join(config.pre_path, zp_meta_name)
        zp.write(meta_file, zp_meta_name)
    except Exception as e:
        logger.error("ERROR - zip error occured: %s" % str(e))
    finally:
        logger.critical("-----zip file stop-----")
        zp.close()
    return zip_name

def process_set(set_name):
    '''
    Increase data set by labeling the inbetween frames
    '''
    data_path = os.path.join(config.pre_path, set_name)
    label_path = os.path.join(set_name, set_name+'.csv')
    label_path = os.path.join(config.pre_path, label_path)

    cam_1_path = os.path.join(data_path, '1')
    cam_1_files = os.listdir(cam_1_path)
    cam_1_files.sort()
    cam_1_files = deque(cam_1_files)
    cam_2_path = os.path.join(data_path, '2')
    cam_2_files = os.listdir(cam_2_path)
    cam_2_files.sort()
    cam_2_files = deque(cam_2_files)

    df = pd.read_csv(label_path, names=['cam_1', 'cam_2', 'action'])

    entries = []
    ind = 2
    st_ind = 1
    end_ind = -1
    ranges = []
    if ind >= len(df.index):
        ranges.append([st_ind, st_ind])
    else:
        while ind < len(df.index):
            if df['action'].iloc[st_ind] == df['action'].iloc[ind]:
                end_ind = ind
            else:
                if end_ind >= 0:
                    ranges.append([st_ind, end_ind])
                else:
                    ranges.append([st_ind, st_ind])
                st_ind = ind
                end_ind = -1
            if ind == len(df.index) - 1:
                if (end_ind >= 0):
                    ranges.append([st_ind, end_ind])
                else:
                    ranges.append([st_ind, st_ind])
            ind += 1

    for inds in ranges:
        while cam_1_files and df['cam_1'].iloc[inds[0]] != cam_1_files[0]:
            cam_1_files.popleft()
        while cam_2_files and df['cam_2'].iloc[inds[0]] != cam_2_files[0]:
            cam_2_files.popleft()
        cam_1_list = deque()
        while cam_1_files:
            if df['cam_1'].iloc[inds[1]] != cam_1_files[0]:
                cam_1_list.append(cam_1_files.popleft())
            if df['cam_1'].iloc[inds[1]] == cam_1_files[0]:
                cam_1_list.append(cam_1_files.popleft())
                break
        cam_2_list = deque()
        while cam_2_files:
            if df['cam_2'].iloc[inds[1]] != cam_2_files[0]:
                cam_2_list.append(cam_2_files.popleft())
            if df['cam_2'].iloc[inds[1]] == cam_2_files[0]:
                cam_2_list.append(cam_2_files.popleft())
                break
        while cam_1_list and cam_2_list:
            timestamp = get_ctime(cam_1_path, cam_1_list[0])
            entries.append({
                'timestamp': timestamp,
                'cam_1': cam_1_list[0],
                'cam_2': cam_2_list[0],
                'action': df['action'].iloc[inds[0]]
            })
            cam_1_list.popleft()
            cam_2_list.popleft()
    return entries, cam_1_path, cam_2_path

def main():
    parser = build_parser()
    args = parser.parse_args()

    configure_log(args.log, args.set_name)
    logger.critical("Process Start")
    if not args.set_name:
        logger.error("ERROR - Invalid set name")
        exit(0)
    data_path = os.path.join(config.pre_path, args.set_name)
    label_path = os.path.join(args.set_name, args.set_name+'.csv')
    label_path = os.path.join(config.pre_path, label_path)
    meta_path = os.path.join(args.set_name, args.set_name+'.meta')
    meta_path = os.path.join(config.pre_path, label_path)
    if not os.path.exists(data_path):
        logger.error("ERROR - Unable to find preproc. set: %s" % args.set_name)
        exit(0)
    if not os.path.exists(label_path):
        logger.error("ERROR - Unable to find csv file: %s" % args.set_name)
        exit(0)
    if not os.path.exists(meta_path):
        logger.error("ERROR - Unable to find meta file: %s" % args.set_name)
        exit(0)

    zip_info = process_set(args.set_name)
    zip_file = write_to_zip(args.set_name, zip_info)

    if args.push:
        push_to_cloud(args.set_name, zip_file)
    logger.debug("Process End")

if __name__ == '__main__':
    main()
