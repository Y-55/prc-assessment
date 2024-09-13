import datetime
import random
import time
from prc.redpanda import Producer
import json
import os

from sqlalchemy import select
from kafka import KafkaConsumer

# Create a consumer client
consumer = KafkaConsumer(
    # topic
    "pg.public.hacker_news",
    # consumer configs
    bootstrap_servers=os.getenv("REDPANDA_BROKERS", ""),
    group_id="convert-to-cockroachdb-output-group",
    auto_offset_reset="earliest",
    value_deserializer=lambda v: json.loads(v),
)
redpanda_producer = Producer(topic="news_queue")

# Consume messages from a Redpanda topic
default_state = {
    "id": None,
    "text": None,
    "counter": None,
    "state": None,
    "created_at": None,
    "updated_at": None,
}
default_message = {
    "before": {},
    "after": {},
    "updated": None,
}
latest_state_by_id = {}
is_deleted_by_id = {}
for msg in consumer:
    kafka_message = msg.value
    message = default_message.copy()
    print(kafka_message)
    # after: null
    if kafka_message["op"] == "d":
        message["before"] = {
            "id": kafka_message["before"]["id"],
            "text": latest_state_by_id[kafka_message["before"]["id"]]["text"],
            "counter": latest_state_by_id[kafka_message["before"]["id"]]["counter"],
            "state": latest_state_by_id[kafka_message["before"]["id"]]["state"],
            "created_at": latest_state_by_id[kafka_message["before"]["id"]]["created_at"],
            "updated_at": kafka_message["ts_ms"],
        }
        message["after"] = None
        message["updated"] = int(kafka_message["ts_ms"])
        is_deleted_by_id[kafka_message["before"]["id"]] = True
    # before: null
    elif kafka_message["op"] == "c":
        message["after"] = {
            "id": kafka_message["after"]["id"],
            "text": kafka_message["after"]["text"],
            "counter": kafka_message["after"]["counter"],
            "state": kafka_message["after"]["state"],
            "created_at": int(kafka_message["after"]["created_at"]),
            "updated_at": kafka_message["ts_ms"],
        }
        message["before"] = None
        message["updated"] = int(kafka_message["ts_ms"])
        latest_state_by_id[kafka_message["after"]["id"]] = message["after"].copy()
        is_deleted_by_id[kafka_message["after"]["id"]] = False
    # after: {}, before: {}
    elif kafka_message["op"] == "u":
        latest_state = latest_state_by_id.get(kafka_message["after"]["id"], default_state)
        message["before"] = {
            "id": latest_state["id"],
            "text": latest_state["text"],
            "counter": latest_state["counter"],
            "state": latest_state["state"],
            "created_at": latest_state["created_at"],
            "updated_at": latest_state["updated_at"],
        }
        message["after"] = {
            "id": kafka_message["after"]["id"],
            "text": kafka_message["after"]["text"],
            "counter": kafka_message["after"]["counter"],
            "state": kafka_message["after"]["state"],
            "created_at": kafka_message["after"]["created_at"],
            "updated_at": kafka_message["ts_ms"],
        }
        message["updated"] = kafka_message["ts_ms"]
        latest_state_by_id[kafka_message["after"]["id"]] = message["after"].copy()
    else:
        raise ValueError(f"Operation {kafka_message['op']} not supported")
    print(kafka_message["op"])
    print(message)
    redpanda_producer.produce(value=message)
    time.sleep(1)
