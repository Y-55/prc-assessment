import datetime
import random
import time
from prc.redpanda import Producer

# Create a producer instance
redpanda_producer = Producer(topic="purchases")

# Write a purchase event to Redpanda
for i in range(100):
    message = {
        "id": random.randint(1, 10000),
    }

    redpanda_producer.produce(value=message)
    time.sleep(1)