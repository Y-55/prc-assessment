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
from sys import argv

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
    
def dummy_data(table,num=10, start_idx=0):
    data = []
    for i in range(num):
        d = {
            k: valid_value(v.type)
            for k, v in table.__table__.columns.items()
            if k != 'id'
        }
        d['id'] = start_idx+i+1
        data.append(d)
        
    return data

client.execute(text('ALTER TABLE hacker_news REPLICA IDENTITY FULL'))



def insert_data(data):
    print("inserting data")
    for d in tqdm(data):
        client.insert(HackerNews, d)
    
def update_data(data, deleted_keys):
    print("updating data")
    data_to_choose_from = [d for d in data if d['id'] not in deleted_keys]
    random_data = random.choices(data_to_choose_from, k=len(data_to_choose_from)//4)
    for d in tqdm(random_data):
        random_text = "".join( [random.choice(string.ascii_letters + ' ') for i in range(15)] )
        random_counter = random.randint(0, 10_000)
        random_state = random.choice([True, False])
        client.update(HackerNews, d, {'text': random_text, 'counter': random_counter, 'state': random_state})
    
def delete_data(data, deleted_keys):
    print("deleting data")
    data_to_choose_from = [d for d in data if d['id'] not in deleted_keys]
    random_data = random.choices(data_to_choose_from, k=len(data_to_choose_from)//4)
    for i, d in enumerate(tqdm(random_data)):
        client.delete(HackerNews, {'id': d['id']})
    return data_to_choose_from

def run_simualtion(n, n_seconds, pause_seconds):
    n_total_created = 0
    data = dummy_data(HackerNews, num=n, start_idx=n_total_created)
    insert_data(data)
    n_total_created += len(data)
    
    deleted_keys = []

    total_time = 0
    start_time = time.time()
    
    while total_time < n_seconds:
        rand_choice = random.randint(1, 3)
        if rand_choice == 1:
            update_data(data, deleted_keys=deleted_keys)
        elif rand_choice == 2:
            deleted_data = delete_data(data, deleted_keys=deleted_keys)
            deleted_keys += [d['id'] for d in deleted_data]
        elif rand_choice == 3:
            print("generating data")
            new_data = dummy_data(HackerNews, num=n//4, start_idx=n_total_created)

            insert_data(new_data)

            n_total_created += len(new_data)
            data += new_data
        else:
            raise ValueError("unknown choice")
        
        time.sleep(pause_seconds)
        
        end_time = time.time()
        total_time = end_time - start_time

if __name__ == "__main__":
    n = int(argv[1]) # records created per iteration
    n_seconds = int(argv[2]) # simulation time
    pause_seconds = int(argv[3]) # time after every operation
    time.sleep(5)
    run_simualtion(n=n, n_seconds=n_seconds, pause_seconds=pause_seconds)