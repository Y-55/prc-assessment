import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

import prc
PROJECT_PATH=os.path.dirname(os.path.dirname(os.path.abspath(prc.__file__)))

source_path = PROJECT_PATH+'/connect-configs/postgres-source.json'

source_reader = open(source_path, 'r')

source_name = json.load(source_reader)['name']

DEBEZIUM_HOST = os.getenv('DEBEZIUM_HOST')
DEBEZIUM_PORT = os.getenv('DEBEZIUM_PORT')

r = requests.get(
     f"http://{DEBEZIUM_HOST}:{DEBEZIUM_PORT}/connectors/{source_name}/status",
    headers={'Content-Type': 'application/json'}
)

print(r.text)