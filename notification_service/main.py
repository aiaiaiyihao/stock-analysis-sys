import threading

from fastapi import FastAPI
from sqlalchemy import select

from app.consumer import consume_alerts
from app.database import Base, SessionLocal, engine
from app.models import Notification

app = FastAPI(title="Notification Service")

Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=consume_alerts, daemon=True)
    thread.start()


@app.get("/")
def home():
    return {"message": "Notification service running"}


@app.get("/notifications")
def get_notifications():
    db = SessionLocal()
    try:
        rows = db.execute(
            select(Notification).order_by(Notification.id.desc())
        ).scalars().all()

        return {
            "count": len(rows),
            "items": [
                {
                    "id": row.id,
                    "symbol": row.symbol,
                    "price": row.price,
                    "condition": row.condition,
                    "threshold": row.threshold,
                    "message": row.message,
                    "event_timestamp": row.event_timestamp,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                }
                for row in rows
            ],
        }
    finally:
        db.close()