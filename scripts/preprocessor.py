'''
Checks the preprocess queue for jobs.
Processes jobs(augment/duplicate checks) and push onto bucket
'''

import sys
import os
from os.path import dirname
from os.path import basename
import time
import signal
sys.path.append(dirname(dirname(os.path.realpath(__file__))))

from google.cloud import storage
from google.cooud import datastore

from robocar42 import util
from robocar42.util import progress_bar
from robocar42 import config
from robocar42 import preprocess

logger = util.configure_log('preprocessor')

def query_list():
    '''
    Gets the list of jobs on the preprocess datastore
    '''
    cloud_conf = config.cloud_parser_config('cloud.ini')
    client = datastore.Client(
                namespace=cloud_conf['datastore_namespace'],
                project=cloud_conf['project'])
    ds_query = client.query(kind='preprocess')
    entries = list(ds_query.fetch())
    return entries

def remove_file():
    '''
    Removes files from local machines
    '''
    pass

def update_dataset_table(entity):
    '''
    Update dataset table
    '''
    cloud_conf = config.cloud_parser_config('cloud.ini')
    client = datastore.Client(
                namespace=cloud_conf['datastore_namespace'],
                project=cloud_conf['project'])
    ds_key = client.key('datasets')
    ds_entity = datastore.Entity(ds_key)

    ds_query = client.query(kind='datasets')
    ds_query.add_filter('set_name', '=', entity['set_name'])
    if not list(ds_query.fetch()):
        for key in entity:
            ds_entity[key] = entity[key]
        client.put(ds_entity)
    else:
        logger.warning(
            "Warning - %s entry already exists." % entity['set_name'])

def preproces_set(set_name)
    filename = os.path.join(config.data_path, set_name)
    label_path = os.path.join(set_name, set_name+'.csv')
    label_path = os.path.join(config.data_path, label_path)
    if not os.path.exists(filename) or
        return

def interrupt_handler(signum, frame):
    global interrupted
    interrupted = True
    logger.info("Exiting program...")

if __name__ == '__main__':
    signal.signal(signal.SIGNINT, interrupt_handler)
    interrupted = False
    while not interrupted:
        job_list = query_list()
        for job in job_list:
            #process then remove job from queue
            preprocess_set(job['set_name'])
            update_dataset_table(job)
