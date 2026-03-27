# StockAnalyzer

A real-time stock monitoring system built on a microservices architecture. Supports live price fetching, technical indicator analysis, alert triggering via Kafka, and persistent notifications in PostgreSQL.

---

## System Architecture

```
yfinance API
     ↓
main_service (FastAPI :8000)
     ↓  Alert triggered
Kafka (stock-alerts topic)
     ↓
notification_service (FastAPI :8001)
     ↓
PostgreSQL (notifications table)
     ↑
Dashboard (dashboard.html)
```

---

## Project Structure

```
StockAnalyzer/
├── docker-compose.yml
├── dashboard.html                  # Frontend Dashboard
├── README.md
├── main_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                     # FastAPI entry point
│   ├── fetch.py                    # yfinance data fetching
│   ├── analysis.py                 # Technical indicator calculation
│   ├── alert.py                    # Alert rules and trigger logic
│   └── kafka_producer.py           # Kafka message publisher
└── notification_service/
    ├── Dockerfile
    ├── requirements.txt
    ├── main.py                     # FastAPI entry point
    ├── consumer.py                 # Kafka consumer
    ├── database.py                 # SQLAlchemy database connection
    ├── models.py                   # ORM models
    └── schemas.py                  # Pydantic schemas
```

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- A browser (for the Dashboard)

### Start All Services

```bash
# Clone the repository
git clone <your-repo-url>
cd StockAnalyzer

# Build and start all services
docker-compose up --build
```

Once running, services are available at:

| Service                       | URL                                            |
| ----------------------------- | ---------------------------------------------- |
| main_service                  | http://localhost:8000                          |
| main_service API Docs         | http://localhost:8000/docs                     |
| notification_service          | http://localhost:8001                          |
| notification_service API Docs | http://localhost:8001/docs                     |
| Dashboard                     | Open `dashboard.html` directly in your browser |

### Stop All Services

```bash
docker-compose down
```

---

## API Reference

### main_service (port 8000)

#### `GET /stocks/{symbol}`

Fetches the latest stock price, checks alert rules, and publishes to Kafka if triggered.

**Example Request**

```
GET http://localhost:8000/stocks/AAPL
```

**Example Response**

```json
{
  "symbol": "AAPL",
  "latest_price": 252.89,
  "alert_triggered": true,
  "alert": {
    "symbol": "AAPL",
    "price": 252.89,
    "condition": "above",
    "threshold": 220,
    "message": "AAPL crossed above 220"
  },
  "published_to_kafka": true
}
```

---

#### `GET /stocks/{symbol}/analysis`

Returns technical indicators: SMA5, SMA20, and daily return.

**Example Request**

```
GET http://localhost:8000/stocks/AAPL/analysis
```

**Example Response**

```json
{
  "symbol": "AAPL",
  "latest_close": 252.89,
  "sma_5": 251.33,
  "sma_20": 256.14,
  "daily_return": 0.00107
}
```

---

### notification_service (port 8001)

#### `GET /notifications`

Returns all saved alert notification records from the database.

**Example Response**

```json
{
  "count": 1,
  "items": [
    {
      "id": 1,
      "symbol": "AAPL",
      "price": 252.89,
      "condition": "above",
      "threshold": 220.0,
      "message": "AAPL crossed above 220",
      "event_timestamp": "2026-03-26T23:45:26+00:00",
      "created_at": "2026-03-26T23:45:26+00:00"
    }
  ]
}
```

---

## Alert Rules

Default rules are defined in `main_service/alert.py`:

| Symbol | Condition | Threshold |
| ------ | --------- | --------- |
| AAPL   | Price ≥   | $220      |
| TSLA   | Price ≤   | $150      |
| NVDA   | Price ≥   | $1000     |

> Once an alert is triggered for a symbol, a 1-hour cooldown prevents duplicate alerts. The cooldown resets if the service is restarted.

---

## Dashboard

Open `dashboard.html` directly in your browser — no extra server needed.

**Features:**

- Switch between AAPL / TSLA / NVDA, or type any custom symbol in the search box
- Live stats cards: latest price, SMA5, SMA20, daily return
- Price trend chart (last 5 trading days)
- Moving average chart (SMA5 vs SMA20 vs Close, last 1 month)
- Alert notification history table

> Make sure your Docker containers are running before opening the Dashboard.

**How the frontend connects to the backend:**

The Dashboard uses the browser's `fetch()` API to call your FastAPI services directly:

```javascript
const MAIN = 'http://localhost:8000';
const NOTIF = 'http://localhost:8001';
```

Docker Compose maps container ports to your local machine, so `localhost:8000` reaches the `main_service` container. CORS middleware is required on both FastAPI services to allow the browser to make cross-origin requests from the local HTML file.

---

## Tech Stack

| Layer            | Technology                         |
| ---------------- | ---------------------------------- |
| Web Framework    | FastAPI + Uvicorn                  |
| Stock Data       | yfinance                           |
| Message Queue    | Apache Kafka (Confluent)           |
| Database         | PostgreSQL + SQLAlchemy            |
| Containerization | Docker + Docker Compose            |
| Frontend         | HTML / CSS / JavaScript + Chart.js |

---

## Troubleshooting

**Dashboard shows no data**
Make sure both FastAPI services have CORS middleware enabled and that all Docker containers are running.

**main_service fails to start**
Ensure `kafka-python` is listed in `main_service/requirements.txt`, then run `docker-compose up --build` again.

**notification_service cannot connect to the database**
Check that `DB_HOST` is set to `postgres` (the service name) in `docker-compose.yml` — not `localhost`.

**Duplicate alert notifications keep appearing**
The 1-hour cooldown in `alert.py` prevents repeated alerts, but it resets on service restart. To make the cooldown persistent across restarts, store the last-triggered timestamp in the database instead of in memory.

Yihao Ai Backend Developer