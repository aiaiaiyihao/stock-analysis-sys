from datetime import datetime, timezone

import pandas as pd
import plotly.graph_objects as go
import requests
import yfinance as yf
from fastapi import FastAPI, HTTPException

from alert import check_alert

app = FastAPI(title="Main Stock Service")

NOTIFICATION_URL = "http://127.0.0.1:8001/notify"


def fetch_stock_data(symbol: str, period: str = "1mo") -> pd.DataFrame:
    df = yf.download(symbol, period=period, interval="1d", auto_adjust=False)

    if df.empty:
        raise ValueError(f"No data found for symbol: {symbol}")

    return df


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["SMA_5"] = df["Close"].rolling(5).mean()
    df["SMA_20"] = df["Close"].rolling(20).mean()
    df["Daily_Return"] = df["Close"].pct_change()
    return df


def send_notification(alert_payload: dict) -> dict:
    payload = {
        **alert_payload,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    try:
        response = requests.post(NOTIFICATION_URL, json=payload, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {
            "status": "failed",
            "error": str(exc)
        }


@app.get("/")
def home():
    return {"message": "Main stock service running"}


@app.get("/stocks/{symbol}")
def get_stock(symbol: str):
    try:
        df = fetch_stock_data(symbol.upper(), period="5d")
        latest_price = float(df["Close"].dropna().iloc[-1])
        alert = check_alert(symbol.upper(), latest_price)

        notification_result = None
        if alert:
            notification_result = send_notification(alert)

        return {
            "symbol": symbol.upper(),
            "latest_price": latest_price,
            "alert_triggered": alert is not None,
            "alert": alert,
            "notification_result": notification_result
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/stocks/{symbol}/analysis")
def get_stock_analysis(symbol: str):
    try:
        df = fetch_stock_data(symbol.upper())
        df = add_indicators(df)

        latest_row = df.dropna().iloc[-1]

        return {
            "symbol": symbol.upper(),
            "latest_close": float(latest_row["Close"]),
            "sma_5": float(latest_row["SMA_5"]),
            "sma_20": float(latest_row["SMA_20"]),
            "daily_return": float(latest_row["Daily_Return"]),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/stocks/{symbol}/chart")
def get_stock_chart(symbol: str):
    try:
        df = fetch_stock_data(symbol.upper())
        df = add_indicators(df)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close"))
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA_5"], mode="lines", name="SMA 5"))
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA_20"], mode="lines", name="SMA 20"))

        chart_html = fig.to_html(full_html=False)

        return {
            "symbol": symbol.upper(),
            "chart_html": chart_html
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))