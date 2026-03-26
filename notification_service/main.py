from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Notification Service")

notifications = []


class NotificationRequest(BaseModel):
    symbol: str
    price: float
    condition: str
    threshold: float
    message: str
    timestamp: str


@app.get("/")
def home():
    return {"message": "Notification service running"}


@app.post("/notify")
def notify(payload: NotificationRequest):
    record = {
        "symbol": payload.symbol,
        "price": payload.price,
        "condition": payload.condition,
        "threshold": payload.threshold,
        "message": payload.message,
        "timestamp": payload.timestamp,
        "received_at": datetime.utcnow().isoformat()
    }

    notifications.append(record)

    print(f"[NOTIFICATION] {record['message']} | current price: {record['price']}")

    return {
        "status": "received",
        "delivery": "mock",
        "notification": record
    }


@app.get("/notifications")
def get_notifications():
    return {
        "count": len(notifications),
        "items": notifications
    }