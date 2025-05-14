import json
import os

def load_config(niche):
    config_path = os.path.join('config', f'{niche}.json')
    with open(config_path, 'r') as f:
        return json.load(f)