import json
import os
from kafka import KafkaConsumer

from database import SessionLocal
from models import Notification

BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
ALERT_TOPIC = os.getenv("ALERT_TOPIC", "stock-alerts")


def consume_alerts():
    consumer = KafkaConsumer(
        ALERT_TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="notification-service-group",
    )

    for message in consumer:
        payload = message.value

        db = SessionLocal()
        try:
            notification = Notification(
                symbol=payload["symbol"],
                price=payload["price"],
                condition=payload["condition"],
                threshold=payload["threshold"],
                message=payload["message"],
                event_timestamp=payload["timestamp"],
            )
            db.add(notification)
            db.commit()
            print(f"[NOTIFICATION SAVED] {payload['message']}")
        finally:
            db.close()