from prc.postgres.models.models import HackerNews
from prc.postgres.backend import PostgresSQLAlchemyWrapper as Client
from prc.postgres.backend.types import (
    Integer, 
    String,
    DateTime,
    Boolean
)
from sqlalchemy import text
import random
from datetime import datetime
import time
from tqdm import tqdm

import random
import string

client = Client()

if not client.has_table(HackerNews):
    raise Exception(f"Table {HackerNews.__tablename__} does not exist")

def valid_value(_type):
    if type(_type) == Integer:
        return random.randint(0,1000)
    elif type(_type) == DateTime:
        return datetime.now()
    elif type(_type) == Boolean:
        return random.choice([True,False])
    elif type(_type) == String:
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10))
    else:
        raise ValueError(f"Type {type(_type)} not supported")
    
def dummy_data(table,num=10):
    data = []
    for i in range(num):
        d = {
            k: valid_value(v.type)
            for k, v in table.__table__.columns.items()
            if k != 'id'
        }
        d['id'] = i+1
        data.append(d)
        
    return data


num=100

client.execute(text('ALTER TABLE hacker_news REPLICA IDENTITY FULL'))

print("generating data")
data = dummy_data(HackerNews, num)

print("inserting data")
for d in tqdm(data):
    client.insert(HackerNews, d)
time.sleep(5)
    
print("updating data")
random_data = random.choices(data, k=len(data)//4)
for d in tqdm(random_data):
    random_text = "".join( [random.choice(string.ascii_letters + ' ') for i in range(15)] )
    random_counter = random.randint(0, 10_000)
    random_state = random.choice([True, False])
    client.update(HackerNews, d, {'text': random_text, 'counter': random_counter, 'state': random_state})
time.sleep(5)
    
print("deleting data")
random_data = random.choices(data, k=len(data)//4)
for i, d in enumerate(tqdm(random_data)):
    client.delete(HackerNews, {'id': d['id']})
time.sleep(5)
