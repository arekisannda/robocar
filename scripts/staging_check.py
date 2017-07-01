'''
Inserts items into bigquery
'''

import sys
import os
from os.path import dirname
from os.path import basename
import time
import zipfile
sys.path.append(dirname(dirname(os.path.realpath(__file__))))

from google.cloud import storage
from apiclient import discovery

from robocar42.progressbar import progress_bar
from robocar42 import config

def get_staging():
    '''
    Gets the list of files under the staging folder
    '''
    cloud_conf = config.cloud_parser_config('cloud.ini')
    client = storage.Client()
    bucket = client.get_bucket(cloud_conf['bucket'])
    folder = cloud_conf['folder']+'/'
    blobs = list(bucket.list_blobs(prefix=folder, delimiter='/'))
    return blobs

def download_and_unpack(blob, filename):
    local_filename = os.path.join(config.download_path, filename)
    blob.download_to_filename(local_filename)

    # Completed download
    with zipfile.ZipFile(local_filename) as zp:
        for name in zp.namelist():
            if '.bmp' in name:
                zp.extract(name, config.data_path)
            elif '.csv' in name:
                zp.extract(name, config.label_path)

    #After extraction, delete from bucket and machine intermediary files
    if blob.exists():
        try:
            blob.delete()
        except google.cloud.exceptions.NotFound as err:
            pass

    if os.path.exists(local_filename):
        try:
            os.remove(local_filename)
        except OSError as err:
            pass

if __name__ == '__main__':
    if not os.path.exists(config.download_path):
        os.makedirs(config.download_path)
    while True:
        blobs = get_staging()
        for blob in blobs:
            bname = basename(blob.name)
            if bname:
                # check if file already exists
                no_ext = os.path.splitext(bname)[0]
                ext_path = os.path.join(config.data_path, no_ext)
                if not os.path.exists(ext_path):
                    download_and_unpack(blob, bname)
        #Sleep for 10 seconds after each iteration
        time.sleep(10)