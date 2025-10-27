import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient

# Importiere deine eigenen Funktionen
from data_handler import get_historical_data

# .env-Datei aus dem Hauptverzeichnis laden
dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path=dotenv_path)

# Pydantic models
class SymbolRequest(BaseModel):
    symbol: str

class ChartResponse(BaseModel):
    symbol: str
    tradingview_url: str
    yahoo_finance_url: str
    current_price: float = None
    change_percent: float = None
    formatted_message: str = None  # Ready-to-send WhatsApp message

# Initialize FastAPI and Alpaca clients
app = FastAPI(title="Alpaca Stock Info API")
data_client = StockHistoricalDataClient(
    os.getenv("APCA_API_KEY_ID"),
    os.getenv("APCA_API_SECRET_KEY")
)

@app.post("/chart-links", response_model=ChartResponse)
def get_chart_links(request: SymbolRequest):
    """Returns professional chart links for a stock symbol."""
    symbol = request.symbol.upper()
    
    # Get basic data to verify symbol exists
    stock_df = get_historical_data(data_client, symbol, days_back=5)
    
    if stock_df is None or stock_df.empty:
        raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
    
    # Calculate basic metrics
    latest = stock_df.iloc[-1]
    previous = stock_df.iloc[-2] if len(stock_df) > 1 else latest
    current_price = float(latest['close'])
    change_percent = ((current_price - float(previous['close'])) / float(previous['close'])) * 100
    
    # Format data
    price_rounded = round(current_price, 2)
    change_rounded = round(change_percent, 2)
    
    # Emojis based on performance
    trend_emoji = "🟢" if change_percent >= 0 else "🔴"
    change_sign = "+" if change_percent >= 0 else ""
    
    # TradingView URL
    tv_url = f"https://www.tradingview.com/chart/?symbol={symbol}"
    yf_url = f"https://finance.yahoo.com/quote/{symbol}"
    
    # Create formatted message for WhatsApp
    formatted_msg = f"""📊 *{symbol} Stock Update*

💰 Aktueller Preis: ${price_rounded}
{trend_emoji} Veränderung: {change_sign}{change_rounded}%

🔗 *Charts ansehen:*
📊 TradingView: {tv_url}
📈 Yahoo Finance: {yf_url}

_Powered by StockM8 🚀_"""
    
    return ChartResponse(
        symbol=symbol,
        tradingview_url=tv_url,
        yahoo_finance_url=yf_url,
        current_price=price_rounded,
        change_percent=change_rounded,
        formatted_message=formatted_msg
    )