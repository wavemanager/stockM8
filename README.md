# 📈 StockM8

> AI-powered stock trading assistant with microservice architecture and intelligent orchestration

StockM8 is a production-ready stock market assistant that combines multiple specialized AI agents to provide real-time market analysis, portfolio management, and automated trading through a simple conversational interface.

[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.5-009688.svg)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg)](https://www.python.org/)

---

## 🎯 What is StockM8?

StockM8 is a **microservices-based** trading assistant that uses:

- 🤖 **Google Gemini AI** for intelligent market analysis
- 📊 **Alpaca Markets API** for real-time data & paper trading
- 🎨 **TradingView** for professional chart generation
- 🔀 **Master Orchestrator** for intelligent request routing
- 🔄 **n8n** for workflow automation & chat integration

**Ask in natural language, get professional insights:**

```
"Compare Apple and Tesla"     → Detailed performance comparison
"What's in my portfolio?"     → Account balance & positions
"Buy 5 AAPL at $150"          → Limit order placement
"Show me TSLA chart"          → TradingView chart links
"Should I invest in NVDA?"    → AI-powered analysis
```

---

## 🏗️ Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────┐
│                     User Interface                        │
│              (Telegram / WhatsApp / API)                  │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│                   n8n Workflow Engine                     │
│              (Automation & Integration)                   │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│              Master Orchestrator Agent                    │
│         (Intent Detection & Smart Routing)                │
│                   Port: 8000                              │
└─────┬────────┬──────────┬──────────┬──────────┬─────────┘
      │        │          │          │          │
      ▼        ▼          ▼          ▼          ▼
┌─────────┐ ┌────────┐ ┌───────┐ ┌────────┐ ┌─────────┐
│ Finance │ │ Chart  │ │Portfolio│ │Compare │ │ Order   │
│ Agent   │ │ Agent  │ │ Agent  │ │ Agent  │ │ Agent   │
│ :8001   │ │ :8002  │ │ :8003  │ │ :8004  │ │ :8005   │
└────┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └────┬────┘
     │          │          │          │          │
     └──────────┴──────────┴──────────┴──────────┘
                     │
                     ▼
     ┌────────────────────────────────────────┐
     │      External APIs & Data Sources      │
     │  • Alpaca Markets (Trading & Data)     │
     │  • Google Gemini (AI Analysis)         │
     │  • TradingView (Chart Generation)      │
     └────────────────────────────────────────┘
```

### Microservices Architecture

| Service                 | Technology                 | Port | Purpose                       |
| ----------------------- | -------------------------- | ---- | ----------------------------- |
| **Master Orchestrator** | FastAPI + Strategy Pattern | 8000 | Intent detection & routing    |
| **Finance Agent**       | FastAPI + Google Gemini    | 8001 | AI-powered market analysis    |
| **Chart Agent**         | FastAPI + TradingView API  | 8002 | Chart generation & price data |
| **Portfolio Agent**     | FastAPI + Alpaca API       | 8003 | Account & position tracking   |
| **Comparison Agent**    | FastAPI + Pandas           | 8004 | Stock performance comparison  |
| **Ordering Agent**      | FastAPI + Alpaca Trading   | 8005 | Order placement & management  |
| **n8n**                 | Node.js Workflow Engine    | 5678 | Automation & integrations     |

---

## 🛠️ Technology Stack

### Backend

- **FastAPI**: Modern async Python web framework
  - Automatic OpenAPI documentation
  - Pydantic validation
- **Agno Framework** - AI agent orchestration and tool integration
- **Uvicorn** - High-performance ASGI server
- **Pydantic** - Automatic JSON validation

### AI´s & (future Machine Learning Models)

- **Google Gemini flash-2.0**: Advanced LLM for market analysis
- **YFinance Tools**: Real-time market data access
- **(Trained Models in future...)**

### Trading & Market Data

- **Alpaca Markets API**: Commission-free trading
  - Paper trading environment (no real money)
  - Real-time market data
  - **Pandas** - Financial data processing

### Infrastructure & Automation

- **Docker & Docker Compose**: Containerized microservices
- **n8n**
- **Telegram/WhatsApp APIs** - Multi-platform chat integration
- **Localtunnel** - Secure webhook tunneling

---

## ✨ Features

### 🧠 Master Orchestrator

**Intelligent Intent Detection using Strategy Pattern**

The orchestrator analyzes user input and routes to the appropriate expert:

```python
# Intent Detection Examples
"Compare Apple and Tesla"     → comparison_agent
"What's in my portfolio?"     → portfolio_agent
"Buy 5 AAPL"                  → ordering_agent (market)
"Buy TSLA at $240"            → ordering_agent (limit)
"Show me MSFT chart"          → chart_agent
"Is the market open?"         → market_status_agent
"Should I invest in NVDA?"    → finance_agent (AI)
```

**Key Features:**

- ✅ Pattern-based intent classification
- ✅ Automatic stock symbol extraction (company names → tickers)
- ✅ Order parameter parsing (quantity, price, side)
- ✅ Graceful fallback to AI agent
- ✅ Health monitoring of all experts

### 🎯 Specialized Agents

#### 1. 🤖 Finance Agent (AI Analysis)

- **Technology**: Google Gemini 2.0 + YFinance
- **Capabilities**:
  - Fundamental analysis
  - Technical indicators
  - Market sentiment analysis
  - Investment recommendations
- **Output**: Telegram-optimized formatted text

#### 2. 📊 Chart Agent

- **Technology**: TradingView Widget API
- **Capabilities**:
  - Multiple timeframe charts (1D, 1W, 1M, 1Y, 5Y)
  - Technical indicators overlay
  - Real-time price data
- **Output**: Chart URLs + price info

#### 3. 💼 Portfolio Agent

- **Technology**: Alpaca Trading API
- **Capabilities**:
  - Real-time account balance
  - Current positions & P&L
  - Buying power calculation
  - Portfolio allocation breakdown
- **Output**: Formatted portfolio summary

#### 4. 🔍 Comparison Agent

- **Technology**: Alpaca Data API + Pandas
- **Capabilities**:
  - Side-by-side stock comparison
  - Performance metrics (1D, 1W, 1M)
  - Price change calculations
  - Winner determination
- **Output**: Comparative analysis

#### 5. 💰 Ordering Agent

- **Technology**: Alpaca Trading API
- **Capabilities**:
  - Market orders (instant execution)
  - Limit orders (price-specific)
  - GTC (Good-Till-Canceled) orders
  - Market status awareness
- **Output**: Order confirmation + status

#### 6. 🕐 Market Status Agent

- **Technology**: Alpaca Clock API
- **Capabilities**:
  - Real-time market open/closed status
  - Next open/close timestamps
  - Trading hours information
- **Output**: Market status summary

---

## 🚀 Quick Start

### Prerequisites

- **Docker** 20.10+ & **Docker Compose** 2.0+
- **Alpaca Markets** account ([Sign up free](https://alpaca.markets))
- **Google AI Studio** API key ([Get key](https://aistudio.google.com/app/apikey))
- Optional: **Telegram Bot** token ([Create bot](https://t.me/botfather))

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/wavemanager/stock_m8.git
   cd stock_m8
   ```

2. **Configure environment variables**
   ```bash
   cp .env_example .env
   ```
