import datetime
import random
import time
from prc.redpanda import Producer

# Create a producer instance
redpanda_producer = Producer(topic="purchases")

# Write a purchase event to Redpanda
for i in range(100):
    # dynamic values
    original_state = {
        "created_at": datetime.datetime.now().isoformat(),
        "device_id": f"{random.randint(1, 10000)}",
        "device_os": "ios",
        "language": "ar",
        "notification_token": f"{random.randint(1, 10000)}",
        "push_enabled": True,
        "subscriber_id": None,
        "updated_at": datetime.datetime.now().isoformat(),
        "user_id": f"{random.randint(1, 10)}",
    }
    
    message = {
        "after": {
            "created_at": original_state["created_at"],
            "device_id": original_state["device_id"],
            "device_os": original_state["device_os"],
            "language": original_state["language"],
            "notification_token": original_state["notification_token"],
            "push_enabled": original_state["push_enabled"],
            "subscriber_id": original_state["subscriber_id"],
            "updated_at": original_state["updated_at"],
            "user_id": original_state["user_id"],
        },
        "before": {
            "created_at": original_state["created_at"],
            "device_id": original_state["device_id"],
            "device_os": original_state["device_os"],
            "language": original_state["language"],
            "notification_token": original_state["notification_token"],
            "push_enabled": original_state["push_enabled"],
            "subscriber_id": original_state["subscriber_id"],
            "updated_at": original_state["updated_at"],
            "user_id": original_state["user_id"],
        },
        "updated": f"{random.randint(1, 10000)}.0000000000",
        
    }

    redpanda_producer.produce(value=message)
    time.sleep(1)