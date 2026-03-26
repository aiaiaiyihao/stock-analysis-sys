import json
import os
from kafka import KafkaProducer

BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
ALERT_TOPIC = os.getenv("ALERT_TOPIC", "stock-alerts")

# 改成懒加载，不在模块级别直接连接
_producer = None

def get_producer():
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
    return _producer


def publish_alert_event(payload: dict) -> None:
    producer = get_producer()
    producer.send(ALERT_TOPIC, payload)
    producer.flush()