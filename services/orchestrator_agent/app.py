import os
import re
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional, Dict, List, Callable

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path=dotenv_path)

app = FastAPI(title="Master Orchestrator Agent")

# Expert agent endpoints (Docker internal network)
EXPERT_URLS = {
    "finance": "http://agent-01:80/ask",
    "chart": "http://stock-chart-agent:80/chart-links",
    "portfolio": "http://alpaca-account:80/account-info",
    "comparison": "http://stock-comparison:80/compare",
    "market_order": "http://stock-ordering:80/order/market",
    "limit_order": "http://stock-ordering:80/order/limit",
    "market_status": "http://stock-ordering:80/market-status"
}

# Company name to ticker symbol mapping
COMPANY_TO_TICKER = {
    "apple": "AAPL", "tesla": "TSLA", "microsoft": "MSFT",
    "google": "GOOGL", "alphabet": "GOOGL", "amazon": "AMZN",
    "meta": "META", "facebook": "META", "nvidia": "NVDA",
    "netflix": "NFLX", "amd": "AMD", "intel": "INTC",
    "ford": "F", "gm": "GM", "general motors": "GM",
    "disney": "DIS", "coca cola": "KO", "pepsi": "PEP"
}

# Intent detection patterns (keyword → intent mapping)
INTENT_PATTERNS = {
    "market_status": ["market open", "market closed", "börse", "trading hours", "market status"],
    "portfolio": ["portfolio", "account", "balance", "positions", "holdings", "my stocks"],
    "comparison": ["compare", "vs", "versus", "against", "better than", "vergleich", "oder"],
    "ordering": ["buy", "sell", "purchase", "kaufe", "verkaufe"],
    "chart": ["chart", "graph", "visualize", "show", "price", "diagramm"]
}


class UserRequest(BaseModel):
    message: str


class OrchestratorResponse(BaseModel):
    response: str
    agent_used: str
    extracted_data: Optional[Dict] = None


# ============================================================================
# DATA EXTRACTION
# ============================================================================

def extract_stock_symbols(user_message: str) -> List[str]:
    """Extract ticker symbols from user message"""
    message_lower = user_message.lower()
    found_symbols = []
    
    # Find uppercase ticker symbols (1-5 chars)
    ticker_pattern = r'\b[A-Z]{1,5}\b'
    found_symbols.extend(re.findall(ticker_pattern, user_message))
    
    # Find company names
    for company_name, ticker in COMPANY_TO_TICKER.items():
        if company_name in message_lower:
            found_symbols.append(ticker)
    
    return list(set(found_symbols))


def extract_quantity(user_message: str) -> int:
    """Extract quantity from message, default to 1"""
    match = re.search(r'\b(\d+)\b', user_message)
    return int(match.group(1)) if match else 1


def extract_price(user_message: str) -> Optional[float]:
    """Extract price from message like 'at $150' or 'for 150.50'"""
    patterns = [
        r'\$\s*(\d+\.?\d*)',  # $150 or $150.50
        r'at\s+(\d+\.?\d*)',  # at 150
        r'for\s+(\d+\.?\d*)' # for 150
    ]
    
    for pattern in patterns:
        match = re.search(pattern, user_message.lower())
        if match:
            return float(match.group(1))
    
    return None


def extract_order_side(user_message: str) -> str:
    """Determine buy or sell"""
    buy_keywords = ["buy", "purchase", "kaufe"]
    return "buy" if any(kw in user_message.lower() for kw in buy_keywords) else "sell"


# ============================================================================
# INTENT DETECTION (Clean Version)
# ============================================================================

def detect_intent(user_message: str) -> str:
    """
    Detect user intent using pattern matching
    Returns: intent name or 'finance' as default
    """
    message_lower = user_message.lower()
    
    # Check each intent pattern
    for intent_name, keywords in INTENT_PATTERNS.items():
        if any(keyword in message_lower for keyword in keywords):
            # Special validation for intents that need extracted data
            if intent_name == "comparison":
                if len(extract_stock_symbols(user_message)) >= 2:
                    return intent_name
            elif intent_name == "chart":
                if len(extract_stock_symbols(user_message)) >= 1:
                    return intent_name
            else:
                return intent_name
    
    return "finance"  # Default: AI agent


# ============================================================================
# AGENT HANDLERS (Strategy Pattern)
# ============================================================================

def handle_market_status(user_message: str) -> OrchestratorResponse:
    """Handle market status request"""
    response = requests.get(EXPERT_URLS["market_status"], timeout=10)
    response.raise_for_status()
    result = response.json()
    
    return OrchestratorResponse(
        response=result["formatted_message"],
        agent_used="market_status_agent"
    )


def handle_portfolio(user_message: str) -> OrchestratorResponse:
    """Handle portfolio request"""
    response = requests.get(EXPERT_URLS["portfolio"], timeout=10)
    response.raise_for_status()
    result = response.json()
    
    return OrchestratorResponse(
        response=result["formatted_message"],
        agent_used="portfolio_agent"
    )


def handle_comparison(user_message: str) -> OrchestratorResponse:
    """Handle stock comparison request"""
    symbols = extract_stock_symbols(user_message)
    
    if len(symbols) < 2:
        return OrchestratorResponse(
            response="❌ Need 2 stocks to compare. Example: 'Compare AAPL and TSLA'",
            agent_used="orchestrator_validation"
        )
    
    response = requests.post(
        EXPERT_URLS["comparison"],
        json={"symbol1": symbols[0], "symbol2": symbols[1]},
        timeout=10
    )
    response.raise_for_status()
    result = response.json()
    
    return OrchestratorResponse(
        response=result["formatted_message"],
        agent_used="comparison_agent",
        extracted_data={"symbols": symbols[:2]}
    )


def handle_chart(user_message: str) -> OrchestratorResponse:
    """Handle chart request"""
    symbols = extract_stock_symbols(user_message)
    
    if not symbols:
        return OrchestratorResponse(
            response="❌ Which stock? Example: 'Show me AAPL chart'",
            agent_used="orchestrator_validation"
        )
    
    response = requests.post(
        EXPERT_URLS["chart"],
        json={"symbol": symbols[0]},
        timeout=10
    )
    response.raise_for_status()
    result = response.json()
    
    return OrchestratorResponse(
        response=result["formatted_message"],
        agent_used="chart_agent",
        extracted_data={"symbol": symbols[0]}
    )


def handle_ordering(user_message: str) -> OrchestratorResponse:
    """Handle buy/sell order request"""
    symbols = extract_stock_symbols(user_message)
    
    if not symbols:
        return OrchestratorResponse(
            response="❌ Which stock? Example: 'Buy 5 AAPL'",
            agent_used="orchestrator_validation"
        )
    
    symbol = symbols[0]
    qty = extract_quantity(user_message)
    side = extract_order_side(user_message)
    limit_price = extract_price(user_message)
    
    # Choose endpoint based on price
    endpoint = EXPERT_URLS["limit_order"] if limit_price else EXPERT_URLS["market_order"]
    payload = {"symbol": symbol, "qty": qty, "side": side}
    
    if limit_price:
        payload["limit_price"] = limit_price
    
    response = requests.post(endpoint, json=payload, timeout=10)
    response.raise_for_status()
    result = response.json()
    
    agent_type = "limit_order_agent" if limit_price else "market_order_agent"
    
    return OrchestratorResponse(
        response=result["formatted_message"],
        agent_used=agent_type,
        extracted_data=payload
    )


def handle_finance(user_message: str) -> OrchestratorResponse:
    """Handle general finance/AI request"""
    response = requests.post(
        EXPERT_URLS["finance"],
        json={"prompt": user_message},
        timeout=30
    )
    response.raise_for_status()
    result = response.json()
    
    return OrchestratorResponse(
        response=result.get("response", result.get("formatted_message", "No response")),
        agent_used="finance_agent"
    )


# ============================================================================
# INTENT HANDLER MAPPING (The Magic! 🎯)
# ============================================================================

INTENT_HANDLERS: Dict[str, Callable[[str], OrchestratorResponse]] = {
    "market_status": handle_market_status,
    "portfolio": handle_portfolio,
    "comparison": handle_comparison,
    "chart": handle_chart,
    "ordering": handle_ordering,
    "finance": handle_finance
}


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

@app.post("/orchestrate", response_model=OrchestratorResponse)
def orchestrate_request(request: UserRequest):
    """
    Main orchestrator endpoint - routes user requests to appropriate expert agents
    
    Examples:
        "What's in my portfolio?" → portfolio agent
        "Compare Apple and Tesla" → comparison agent
        "Show me AAPL chart" → chart agent
        "Buy 5 AAPL at $150" → limit order agent
        "Buy 5 AAPL" → market order agent
        "Is the market open?" → market status agent
        "Should I buy Tesla?" → finance agent (AI)
    """
    try:
        user_message = request.message
        intent = detect_intent(user_message)
        
        # Get handler function and execute (ONE LINE!)
        handler = INTENT_HANDLERS.get(intent, handle_finance)
        return handler(user_message)
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503,
            detail=f"Expert agent unavailable: {str(e)}"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Orchestration error: {str(e)}"
        )


@app.get("/")
def health_check():
    """Health check and available experts"""
    return {
        "status": "Master Orchestrator running",
        "available_intents": list(INTENT_HANDLERS.keys()),
        "endpoints": {
            "orchestrate": "/orchestrate",
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.get("/health")
def detailed_health():
    """Check health of all expert agents"""
    health_status = {}
    
    for agent_name, url in EXPERT_URLS.items():
        try:
            # Try to reach the agent (timeout 2 seconds)
            base_url = url.rsplit('/', 1)[0]  # Get base URL
            response = requests.get(base_url, timeout=2)
            health_status[agent_name] = "healthy" if response.status_code == 200 else "degraded"
        except:
            health_status[agent_name] = "unavailable"
    
    all_healthy = all(status == "healthy" for status in health_status.values())
    
    return {
        "orchestrator": "healthy",
        "experts": health_status,
        "overall_status": "healthy" if all_healthy else "degraded"
    }


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🤖 Master Orchestrator Agent")
    print("="*60)
    print(f"\n📍 Available Intents: {list(INTENT_HANDLERS.keys())}")
    print("📍 Server: http://localhost:80")
    print("📚 API Docs: http://localhost:80/docs")
    print("\n💡 Example Request:")
    print('   curl -X POST http://localhost:80/orchestrate \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"message": "Compare Apple and Tesla"}\'')
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=80)
