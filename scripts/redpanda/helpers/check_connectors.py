
import os
import requests
from dotenv import load_dotenv

load_dotenv()
DEBEZIUM_HOST = os.getenv('DEBEZIUM_HOST')
DEBEZIUM_PORT = os.getenv('DEBEZIUM_PORT')

r = requests.get(
    f"http://{DEBEZIUM_HOST}:{DEBEZIUM_PORT}/connectors"
)

print(r.text)