import os
from os.path import dirname
import configparser
from CustomException import ValidationError

ROOT_DIR = os.path.expanduser(dirname(dirname(__file__)))

config = configparser.ConfigParser()

config_path = os.path.join(ROOT_DIR,"config")
data_path = os.path.join(ROOT_DIR,"data_sets")
label_path = os.path.join(ROOT_DIR,"data_labels")
stream_path = os.path.join(ROOT_DIR,"stream")
model_path = os.path.join(ROOT_DIR,"models")

# all paths must exist to project to fully work
if not os.path.exists(config_path):
	raise ValidationError("Director: config path does nto exist.")
if not os.path.exists(data_path):
	raise ValidationError("Directory: data_sets path does not exist.")
if not os.path.exists(label_path):
	raise ValidationError("Directory: data_labels path does not exist.")
if not os.path.exists(stream_path):
	raise ValidationError("Directory: stream path does not exist.")
if not os.path.exists(model_path):
	raise ValidationError("Directory: models path does not exist.")

"""
	Loads configuration file for the program
"""
def vehicle_parser_config(config_name):
	config_file = os.path.join(config_path,config_name)
	config.read(config_file)
	cfg = {}
	vehicle = config['vehicle']
	cfg['car_url'] = vehicle.get('url')
	cfg['straight'] = vehicle.get('straight')
	cfg['left'] = vehicle.get('max_left')
	cfg['right'] = vehicle.get('max_right')
	cfg['exp'] = vehicle.get('exp')
	cfg['speed'] = vehicle.get('speed')
	return cfg

def camera_parser_config(config_name):
	config_file = os.path.join(config_path, config_name)
	config.read(config_file)
	cfg = {}
	camera = config['camera']
	tmp = map(str,camera.get('url_list').split(','))
	tmp = [x.strip() for x in tmp]
	cfg['cam_urls'] = tmp
	cfg['cam_protocol'] = camera.get('protocol')
	cfg['cam_user'] = camera.get('user')
	cfg['cam_pass'] = camera.get('pass')
	cfg['cam_channel'] = camera.get('channel')
	return cfg

def display_parser_config(config_name):
	config_file = os.path.join(config_path, config_name)
	config.read(config_file)
	cfg = {}
	image = config['image']
	cfg['oshape'] = (image.getint('oshapeX'),
					image.getint('oshapeY'))
	cfg['sshape'] = (image.getint('sshapeX'),
					image.getint('sshapeY'))
	cfg['doshape'] = (image.getint('doshapeX'),
					image.getint('doshapeY'))
	cfg['sdshape'] = (image.getint('sdshapeX'),
					image.getint('sdshapeY'))
	return cfg