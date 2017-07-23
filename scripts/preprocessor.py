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
from google.cloud import datastore
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

from robocar42 import util
from robocar42.util import progress_bar
from robocar42 import config
from robocar42 import preprocess

logger = util.configure_log('preprocessor')
cloud_conf = config.cloud_parser_config('cloud.ini')

def query_list():
    '''
    Gets the list of jobs from the preprocess queue
    '''
    cloud_conf = config.cloud_parser_config('cloud.ini')
    client = datastore.Client(
                namespace=cloud_conf['datastore_namespace'],
                project=cloud_conf['datastore_project'])
    ds_query = client.query(kind='preprocess')
    entries = list(ds_query.fetch())
    return entries

def remove_dataset(set_list):
    '''
    Removes files from local machine
    '''


def update_dataset_table(entity):
    '''
    Update dataset table
    '''
    cloud_conf = config.cloud_parser_config('cloud.ini')
    client = datastore.Client(
                namespace=cloud_conf['datastore_namespace'],
                project=cloud_conf['datastore_project'])
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

def preprocess_set(set_list, job_name):
    '''
    performs preprocessing on the unprocessed datasets.
    '''
    options = PipelineOptions()
    google_cloud_options = optinos.view_as(GoogleCloudOptions)
    google_cloud_options.project = cloud_conf['datastore_project']
    google_cloud_options.job_name = job_name
    google_cloud_options.staging_location = cloud_conf['staging']
    google_cloud_options.temp_location = cloud_conf['tmp']
    options.view_as(StandardOptions).runner = 'DataflowRunner'

    with beam.Pipeline(options=options) as p:
        p

def get_working_set(set_list):
    '''
    Generate working set for dataflow pipeline
    '''
    ret_set = []
    for set_item in set_list:
        set_name = set_item['set_name']
        data_path = os.path.join(config.data_path, set_name)
        label_path = os.path.join(set_name, set_name+'.csv')
        label_path = os.path.join(config.data_path, label_path)
        if os.path.exists(data_path) or os.path.exists(label_path):
            ret_set.append(set_name)
    return ret_set

def interrupt_handler(signum, frame):
    global interrupted
    interrupted = True
    logger.info("Exiting program...")

if __name__ == '__main__':
    signal.signal(signal.SIGINT, interrupt_handler)
    interrupted = False
    while not interrupted:
        job_list = query_list()
        working_set = get_working_set(job_list)
        # preprocess_set(working_set, job_name)
        # remove_dataset(working_set)

