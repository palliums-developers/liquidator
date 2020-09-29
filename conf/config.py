import os
import json

URL = "http://47.93.114.230:50001"

config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), './config.json'))

def read_config():
  if os.path.isfile(config_path):
    with open(config_path) as json_file:
      config = json.load(json_file)
    return config
  return dict()

def update_config(config):
  with open(config_path, "w") as json_file:
    json.dump(config, json_file, indent=4)

config = read_config()

