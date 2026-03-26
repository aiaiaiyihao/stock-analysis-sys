import json
import os
from kafka import KafkaProducer

BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
ALERT_TOPIC = os.getenv("ALERT_TOPIC", "stock-alerts")

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)


def publish_alert_event(payload: dict) -> None:
    producer.send(ALERT_TOPIC, payload)
    producer.flush()