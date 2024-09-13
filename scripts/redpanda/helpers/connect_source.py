
import os
import requests
from dotenv import load_dotenv

load_dotenv()
import prc
PROJECT_PATH=os.path.dirname(os.path.dirname(os.path.abspath(prc.__file__)))

source_path = PROJECT_PATH+'/connect-configs/postgres-source.json'

data = open(source_path, 'r').read()

DEBEZIUM_HOST = os.getenv('DEBEZIUM_HOST')
DEBEZIUM_PORT = os.getenv('DEBEZIUM_PORT')
     

r = requests.post(
    f"http://{DEBEZIUM_HOST}:{DEBEZIUM_PORT}/connectors", 
    data=data, 
    headers={'Content-Type': 'application/json'}
)

print(r.text)
