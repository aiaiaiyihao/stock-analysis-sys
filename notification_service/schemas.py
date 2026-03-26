from pydantic import BaseModel


class NotificationPayload(BaseModel):
    symbol: str
    price: float
    condition: str
    threshold: float
    message: str
    timestamp: str