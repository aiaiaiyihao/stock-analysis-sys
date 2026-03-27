# StockAnalyzer

A real-time stock monitoring system built on a microservices architecture. Supports live price fetching, technical indicator analysis, Kafka-driven alert pipelines, persistent notifications in PostgreSQL, and an AI-powered stock assistant powered by LangChain and Ollama.

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

chat_service (FastAPI :8002)
  ├── LangChain Agent + Ollama (LLaMA 3.1)
  ├── Tool: get_stock_price     → main_service
  ├── Tool: get_top_movers      → yfinance
  └── Tool: get_notifications   → notification_service

Dashboard (dashboard.html)
  ├── Price & SMA charts (Chart.js)
  ├── Alert notification table
  └── AI Chat Assistant
```

---

## Project Structure

```
StockAnalyzer/
├── docker-compose.yml
├── .env                            # OLLAMA_BASE_URL (optional)
├── dashboard.html                  # Frontend Dashboard
├── README.md
├── main_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                     # FastAPI entry point
│   ├── fetch.py                    # yfinance data fetching
│   ├── analysis.py                 # Technical indicator calculation
│   ├── alert.py                    # Alert rules and cooldown logic
│   └── kafka_producer.py           # Kafka message publisher
├── notification_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                     # FastAPI entry point
│   ├── consumer.py                 # Kafka consumer
│   ├── database.py                 # SQLAlchemy database connection
│   ├── models.py                   # ORM models
│   └── schemas.py                  # Pydantic schemas
└── chat_service/
    ├── Dockerfile
    ├── requirements.txt
    ├── main.py                     # FastAPI entry point
    ├── agent.py                    # LangChain ReAct agent
    └── tools.py                    # Custom LangChain tools
```

---

## Getting Started

### Prerequisites

- Docker & Docker Compose
- [Ollama](https://ollama.com) installed and running locally
- A browser (for the Dashboard)

### 1. Install and Start Ollama

```bash
# Install Ollama (Mac)
brew install ollama

# Pull the model
ollama pull llama3.1

# Start Ollama
ollama serve
```

### 2. Start All Services

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
| chat_service                  | http://localhost:8002                          |
| chat_service API Docs         | http://localhost:8002/docs                     |
| Dashboard                     | Open `dashboard.html` directly in your browser |

### 3. Stop All Services

```bash
docker-compose down
```

---

## API Reference

### main_service (port 8000)

#### `GET /stocks/{symbol}`

Fetches the latest stock price, evaluates alert rules, and publishes to Kafka if triggered.

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

#### `GET /stocks/{symbol}/analysis`

Returns technical indicators: SMA5, SMA20, and daily return.

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

Returns all saved alert notification records ordered by most recent.

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

### chat_service (port 8002)

#### `POST /chat`

Send a natural language message to the AI stock assistant. Supports conversation history.

**Request Body**

```json
{
  "message": "今天涨幅最大的股票是哪些？",
  "history": []
}
```

**Example Response**

```json
{
  "reply": "今日涨幅最大的股票：\n▲ NVDA: $875.40 (+3.21%)\n▲ META: $512.30 (+2.87%)..."
}
```

**Example prompts:**

- `"今天涨幅最大的股票"` — top gainers from a watchlist of 20 stocks
- `"AAPL 现在多少钱"` — latest price and technical indicators
- `"有哪些 Alert 记录"` — recent alert notification history
- `"特斯拉现在的价格"` — supports Chinese company name mapping

---

## Alert Rules

Default rules defined in `main_service/alert.py`:

| Symbol | Condition | Threshold |
| ------ | --------- | --------- |
| AAPL   | Price ≥   | $220      |
| TSLA   | Price ≤   | $150      |
| NVDA   | Price ≥   | $1000     |

> A 1-hour cooldown prevents duplicate alerts for the same symbol. The cooldown resets on service restart. To persist cooldown state across restarts, store the last-triggered timestamp in the database.

---

## AI Stock Assistant

The chat assistant is powered by a **LangChain ReAct Agent** running **LLaMA 3.1** locally via Ollama. It has access to three custom tools:

| Tool                | Description                                                  |
| ------------------- | ------------------------------------------------------------ |
| `get_stock_price`   | Fetches latest price, SMA5, SMA20, daily return, and alert status for any symbol |
| `get_top_movers`    | Scans a watchlist of 20 stocks and ranks by daily % change   |
| `get_notifications` | Retrieves alert history from the notification service        |

The agent reasons step-by-step (ReAct pattern) and responds in Chinese. It also maps common Chinese company names to ticker symbols (e.g. 苹果 → AAPL, 特斯拉 → TSLA, 英伟达 → NVDA).

---

## Dashboard

Open `dashboard.html` directly in your browser — no extra server needed.

**Features:**

- Quick-select buttons for AAPL, TSLA, NVDA — or type any symbol in the search box
- Live stat cards: latest price, SMA5, SMA20, daily return with trend indicators
- Price trend chart (last 5 trading days)
- Moving average chart — SMA5 vs SMA20 vs Close (last 1 month)
- Alert notification history table
- Embedded AI chat assistant (bottom-right corner)

**How the frontend connects to the backend:**

The Dashboard calls the FastAPI services directly from the browser using `fetch()`:

```javascript
const MAIN = 'http://localhost:8000';
const NOTIF = 'http://localhost:8001';
const CHAT = 'http://localhost:8002';
```

Docker Compose maps container ports to localhost. CORS middleware is enabled on all three services to allow cross-origin requests from the local HTML file.

---

## Tech Stack

| Layer            | Technology                         |
| ---------------- | ---------------------------------- |
| Web Framework    | FastAPI + Uvicorn                  |
| Stock Data       | yfinance                           |
| Message Queue    | Apache Kafka (Confluent)           |
| Database         | PostgreSQL + SQLAlchemy            |
| AI Agent         | LangChain + Ollama (LLaMA 3.1)     |
| Containerization | Docker + Docker Compose            |
| Frontend         | HTML / CSS / JavaScript + Chart.js |

---

## Troubleshooting

**Dashboard shows no data**
Ensure CORS middleware is added to all three FastAPI services and all Docker containers are running.

**main_service fails to start**
Make sure `kafka-python` is in `main_service/requirements.txt`, then rebuild with `docker-compose up --build`.

**notification_service cannot connect to the database**
Set `DB_HOST` to `postgres` (the Docker service name) in `docker-compose.yml`, not `localhost`.

**chat_service returns "request failed"**
Check that Ollama is running locally (`ollama serve`) and the model is pulled (`ollama pull llama3.1`). The container connects to Ollama via `host.docker.internal:11434`.

**Top movers query is slow**
This is expected — the tool fetches data for 20 stocks sequentially from yfinance. Response time is typically 15–30 seconds.

**Duplicate alert notifications**
The 1-hour in-memory cooldown in `alert.py` resets on service restart. Avoid calling `GET /stocks/{symbol}` repeatedly in quick succession, or increase the cooldown window.

**Yihao Ai** Backend Developer