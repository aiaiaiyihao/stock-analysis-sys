# 📊 StockAnalyzer

A real-time stock data analysis system built with microservices architecture. It collects market data, processes indicators, triggers alerts, and visualizes insights through dashboards.

---

## 🚀 System Architecture

The system follows a **microservices + event-driven architecture**:

* **Data Ingestion Service** → Fetches stock data (e.g., yfinance)
* **Processing Service** → Calculates indicators (moving averages, etc.)
* **Notification Service** → Sends alerts based on rules
* **Kafka** → Event streaming between services
* **PostgreSQL** → Persistent storage
* **Redis** → Caching layer
* **Dashboard** → Data visualization

**Data Flow:**

```
Data Source → Ingestion Service → Kafka → Processing Service → Database/Redis
                                              ↓
                                      Notification Service → Alerts
                                              ↓
                                          Dashboard
```

---

## 📁 Project Structure

```
StockAnalyzer/
│
├── ingestion_service/       # Fetch stock data
├── processing_service/      # Data processing & indicators
├── notification_service/   # Alert system
├── common/                 # Shared utilities (models, configs)
├── docker/                 # Docker configs
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd StockAnalyzer
```

### 2. Start infrastructure (Kafka + PostgreSQL + Redis)

```bash
docker-compose up -d
```

### 3. Install dependencies (for each service)

```bash
pip install -r requirements.txt
```

### 4. Run services

Example:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Start each service on different ports:

* ingestion_service → 8000
* processing_service → 8001
* notification_service → 8002

---

## 📡 API Documentation

### 🔹 Example: Fetch Stock Data

**Request:**

```http
GET /stocks/{symbol}
```

**Response:**

```json
{
  "symbol": "AAPL",
  "price": 185.32,
  "timestamp": "2026-03-26T12:00:00Z"
}
```

---

### 🔹 Example: Trigger Alert Rule

**Request:**

```http
POST /alerts
```

```json
{
  "symbol": "AAPL",
  "condition": "price > 200"
}
```

**Response:**

```json
{
  "status": "rule_created"
}
```

---

## 🚨 Alert Rules

Alert rules are based on conditions such as:

* Price thresholds
* Moving average crossover
* Volume spikes

**Example:**

```text
IF price > 200 → Trigger alert
IF MA50 crosses MA200 → Trigger alert
```

Alerts are processed asynchronously via Kafka.

---

## 📊 Dashboard Usage

The dashboard allows you to:

* View real-time stock prices
* Monitor indicators (MA, trends)
* Track triggered alerts
* Analyze historical data

Access via:

```
http://localhost:<dashboard-port>
```

---

## 🧰 Tech Stack

* **Backend:** FastAPI
* **Streaming:** Kafka
* **Database:** PostgreSQL
* **Cache:** Redis
* **Visualization:** Plotly / Dashboard UI
* **Containerization:** Docker

---

## ❓ FAQ

### Q: Should I start Docker first?

Yes. Always run:

```bash
docker-compose up -d
```

before starting FastAPI services.

---

### Q: Can I run services locally without Docker?

Yes, but you still need Kafka, PostgreSQL, and Redis running.

---

### Q: Why is my service not connecting to Kafka/Postgres?

Check:

* Environment variables
* Docker containers are running
* Correct ports (e.g., `localhost:5432`)

---

### Q: Can I extend this system?

Yes! You can add:

* More indicators
* AI/ML models (e.g., prediction)
* Additional notification channels (email, SMS)

---

## ✅ Notes

* Make sure all services use the same Kafka topic configuration
* Use `.env` files for environment variables
* Logging is recommended for debugging distributed systems

---

Yihao Ai Backend Developer