# Master Orchestrator Agent

Central intelligence layer that routes user requests to specialized expert agents.

## Architecture

```
User Message
     ↓
Orchestrator (analyzes intent)
     ↓
  Routes to Expert:
     ├─ Finance Agent (AI analysis)
     ├─ Chart Agent (visualizations)
     ├─ Portfolio Agent (account info)
     ├─ Comparison Agent (stock vs stock)
     ├─ Ordering Agent (buy/sell)
     └─ Market Status (open/closed)
```

## Features

- **Intent Detection**: Analyzes user message to determine goal
- **Symbol Extraction**: Finds stock tickers or company names
- **Smart Routing**: Calls the right expert agent
- **Unified Response**: Returns consistent formatted messages

## Supported Intents

| Intent        | Examples                                   | Expert Used         |
| ------------- | ------------------------------------------ | ------------------- |
| Portfolio     | "What's in my portfolio?", "My balance"    | Portfolio Agent     |
| Comparison    | "Compare AAPL and TSLA", "AAPL vs MSFT"    | Comparison Agent    |
| Charts        | "Show me AAPL chart", "Tesla price"        | Chart Agent         |
| Market Order  | "Buy 5 AAPL", "Sell 10 Tesla"              | Ordering Agent      |
| Limit Order   | "Buy AAPL at $150", "Sell 5 TSLA for $240" | Ordering Agent      |
| Market Status | "Is the market open?", "Trading hours?"    | Market Status Agent |
| AI Analysis   | "Should I buy Tesla?", "Market outlook?"   | Finance Agent       |

## API Endpoints

### POST /orchestrate

Main endpoint - analyzes message and routes to expert

**Request:**

```json
{
  "message": "Compare Apple and Tesla"
}
```

**Response:**

```json
{
  "response": "🔴 STOCK COMPARISON...",
  "agent_used": "comparison_agent",
  "extracted_data": {
    "symbols": ["AAPL", "TSLA"]
  }
}
```

### GET /

Health check and available experts

### GET /health

Detailed health status of all expert agents

## Local Testing

```bash
cd /Users/dilli/UC/stock_m8/services/orchestrator_agent
python3 app.py
```

Then in another terminal:

```bash
# Portfolio query
curl -X POST http://localhost:80/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"message": "What is in my portfolio?"}'

# Stock comparison
curl -X POST http://localhost:80/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"message": "Compare Apple and Tesla"}'

# Chart request
curl -X POST http://localhost:80/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me AAPL chart"}'

# Market order
curl -X POST http://localhost:80/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"message": "Buy 5 AAPL"}'

# Limit order
curl -X POST http://localhost:80/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"message": "Buy 1 TSLA at $240.50"}'

# Market status
curl -X POST http://localhost:80/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"message": "Is the market open?"}'
```

## Docker Deployment

```bash
# Build and start orchestrator
docker-compose up --build orchestrator

# Access at http://localhost:8000
```

## n8n Integration

Super simple workflow:

```
[Telegram Trigger]
    ↓
[HTTP Request Node]
    URL: http://orchestrator:80/orchestrate
    Method: POST
    Body: {"message": "{{$json.message.text}}"}
    ↓
[Send Message Node]
    Text: {{$json.response}}
```

Only 3 nodes needed! The orchestrator handles all routing logic.

## Code Structure

- `extract_stock_symbols()` - Find tickers in message
- `extract_quantity()` - Parse number of shares
- `extract_price()` - Parse limit price if specified
- `is_*_intent()` - Intent detection functions
- `determine_user_intent()` - Main intent analyzer
- `call_*_agent()` - Expert agent API calls
- `orchestrate_request()` - Main routing logic

## Company Name Mapping

Supports natural language company names:

- "Apple" → AAPL
- "Tesla" → TSLA
- "Microsoft" → MSFT
- "Google" or "Alphabet" → GOOGL
- "Meta" or "Facebook" → META
- etc.

## Error Handling

- Missing symbols: Returns helpful validation message
- Agent unavailable: Returns 503 with details
- Timeout: 10s for most calls, 30s for AI agent
- Network errors: Caught and returned as HTTP exceptions
