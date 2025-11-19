from confluent_kafka import Producer
import json
import time
import random
from datetime import datetime,timezone

# 1. Create a Kafka producer instance
producer = Producer({
    "bootstrap.servers":"localhost:9092",
    # value_serializer=lambda v: json.dumps(v).encode("utf-8")
})

# 2. Infinite loop to simulate live banking transactions
while True:
    # 3. Create a fake transaction event
    event = {
        "transaction_id": random.randint(10000000, 99999999),
        "account_id": random.randint(1000, 9999),
        "amount": round(random.uniform(50, 50000), 2),
        "merchant_id": random.choice(["AMAZON", "SWIGGY", "IRCTC", "ZOMATO", "FLIPKART"]),
        "transaction_type": random.choice(["UPI", "CARD", "NETBANKING", "ATM"]),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    # 4. Send event to Kafka topic
    producer.produce(topic="transactions",
        value=json.dumps(event).encode("utf-8"))
    producer.flush()
    # 5. Print it to the console
    print("Sent transaction:", event)

    # 6. Wait 1 second before sending the next event
    time.sleep(1)
