from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from alert import check_alert
from analysis import add_indicators
from fetch import fetch_stock_data
from kafka_producer import publish_alert_event

app = FastAPI(title="Main Stock Service")

# ← 加这段
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Main stock service running"}


@app.get("/stocks/{symbol}")
def get_stock(symbol: str):
    try:
        df = fetch_stock_data(symbol.upper(), period="5d")
        latest_price = float(df["Close"].dropna().iloc[-1].item())  # ← 加 .item()

        alert = check_alert(symbol.upper(), latest_price)
        published = False

        if alert:
            event = {
                **alert,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            publish_alert_event(event)
            published = True

        return {
            "symbol": symbol.upper(),
            "latest_price": latest_price,
            "alert_triggered": alert is not None,
            "alert": alert,
            "published_to_kafka": published
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/stocks/{symbol}/analysis")
def get_stock_analysis(symbol: str):
    try:
        df = fetch_stock_data(symbol.upper(), period="1mo")
        df = add_indicators(df)
        latest_row = df.dropna().iloc[-1]

        return {
            "symbol": symbol.upper(),
            "latest_close": float(latest_row["Close"].item()),      # ← 加 .item()
            "sma_5": float(latest_row["SMA_5"].item()),             # ← 加 .item()
            "sma_20": float(latest_row["SMA_20"].item()),           # ← 加 .item()
            "daily_return": float(latest_row["Daily_Return"].item()) # ← 加 .item()
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))