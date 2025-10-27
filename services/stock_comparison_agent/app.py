import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path=dotenv_path)

app = FastAPI(title="Stock Comparison Agent")

# Initialize Alpaca client
data_client = StockHistoricalDataClient(
    os.getenv("APCA_API_KEY_ID"),
    os.getenv("APCA_API_SECRET_KEY")
)

class ComparisonRequest(BaseModel):
    symbol1: str
    symbol2: str

class StockData(BaseModel):
    symbol: str
    current_price: float
    change_1d: float
    change_1w: float
    change_1m: float

class ComparisonResponse(BaseModel):
    stock1: StockData
    stock2: StockData
    formatted_message: str

def get_stock_data(symbol: str):
    """Holt Preisdaten für ein Symbol und berechnet Performance"""
    try:
        # Zeiträume definieren
        end_date = datetime.now() - timedelta(days=1)  # Paper Trading
        start_date = end_date - timedelta(days=30)
        
        # Daten holen
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=start_date,
            end=end_date
        )
        
        bars = data_client.get_stock_bars(request)
        df = bars.df
        
        if df.empty:
            return None
        
        # Multi-index für ein Symbol auflösen
        if isinstance(df.index, pd.MultiIndex):
            df = df.xs(symbol, level='symbol')
        
        # Preise extrahieren
        current_price = float(df.iloc[-1]['close'])
        price_1d_ago = float(df.iloc[-2]['close']) if len(df) > 1 else current_price
        price_1w_ago = float(df.iloc[-5]['close']) if len(df) > 5 else current_price
        price_1m_ago = float(df.iloc[0]['close'])
        
        # Änderungen berechnen
        change_1d = ((current_price - price_1d_ago) / price_1d_ago) * 100
        change_1w = ((current_price - price_1w_ago) / price_1w_ago) * 100
        change_1m = ((current_price - price_1m_ago) / price_1m_ago) * 100
        
        return {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "change_1d": round(change_1d, 2),
            "change_1w": round(change_1w, 2),
            "change_1m": round(change_1m, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data for {symbol}: {str(e)}")

@app.get("/")
def read_root():
    return {"status": "Stock Comparison Agent is running", "endpoints": ["/compare"]}

@app.post("/compare", response_model=ComparisonResponse)
def compare_stocks(request: ComparisonRequest):
    """Vergleicht zwei Aktien nebeneinander"""
    
    symbol1 = request.symbol1.upper()
    symbol2 = request.symbol2.upper()
    
    # Daten für beide Aktien holen
    stock1_data = get_stock_data(symbol1)
    stock2_data = get_stock_data(symbol2)
    
    if not stock1_data or not stock2_data:
        raise HTTPException(status_code=404, detail="Could not fetch data for one or both symbols")
    
    # Formatierte Nachricht erstellen
    message_parts = []
    
    # Header
    message_parts.append(f"📊 STOCK COMPARISON")
    message_parts.append(f"{symbol1} vs {symbol2}")
    message_parts.append("")
    
    # Vergleichstabelle
    message_parts.append("📈 CURRENT PRICE")
    message_parts.append(f"• {symbol1}: ${stock1_data['current_price']}")
    message_parts.append(f"• {symbol2}: ${stock2_data['current_price']}")
    message_parts.append("")
    
    # 1-Day Performance
    emoji1_1d = "🟢" if stock1_data['change_1d'] >= 0 else "🔴"
    emoji2_1d = "🟢" if stock2_data['change_1d'] >= 0 else "🔴"
    sign1_1d = "+" if stock1_data['change_1d'] >= 0 else ""
    sign2_1d = "+" if stock2_data['change_1d'] >= 0 else ""
    
    message_parts.append("📅 1-DAY CHANGE")
    message_parts.append(f"• {symbol1}: {sign1_1d}{stock1_data['change_1d']}% {emoji1_1d}")
    message_parts.append(f"• {symbol2}: {sign2_1d}{stock2_data['change_1d']}% {emoji2_1d}")
    message_parts.append("")
    
    # 1-Week Performance
    emoji1_1w = "🟢" if stock1_data['change_1w'] >= 0 else "🔴"
    emoji2_1w = "🟢" if stock2_data['change_1w'] >= 0 else "🔴"
    sign1_1w = "+" if stock1_data['change_1w'] >= 0 else ""
    sign2_1w = "+" if stock2_data['change_1w'] >= 0 else ""
    
    message_parts.append("📆 1-WEEK CHANGE")
    message_parts.append(f"• {symbol1}: {sign1_1w}{stock1_data['change_1w']}% {emoji1_1w}")
    message_parts.append(f"• {symbol2}: {sign2_1w}{stock2_data['change_1w']}% {emoji2_1w}")
    message_parts.append("")
    
    # 1-Month Performance
    emoji1_1m = "🟢" if stock1_data['change_1m'] >= 0 else "🔴"
    emoji2_1m = "🟢" if stock2_data['change_1m'] >= 0 else "🔴"
    sign1_1m = "+" if stock1_data['change_1m'] >= 0 else ""
    sign2_1m = "+" if stock2_data['change_1m'] >= 0 else ""
    
    message_parts.append("🗓️ 1-MONTH CHANGE")
    message_parts.append(f"• {symbol1}: {sign1_1m}{stock1_data['change_1m']}% {emoji1_1m}")
    message_parts.append(f"• {symbol2}: {sign2_1m}{stock2_data['change_1m']}% {emoji2_1m}")
    message_parts.append("")
    
    # Winner
    total1 = stock1_data['change_1d'] + stock1_data['change_1w'] + stock1_data['change_1m']
    total2 = stock2_data['change_1d'] + stock2_data['change_1w'] + stock2_data['change_1m']
    
    if total1 > total2:
        winner = f"🏆 {symbol1} is outperforming {symbol2}"
    elif total2 > total1:
        winner = f"🏆 {symbol2} is outperforming {symbol1}"
    else:
        winner = f"⚖️ Both stocks are performing equally"
    
    message_parts.append(winner)
    message_parts.append("")
    message_parts.append("🤖 Powered by StockM8")
    
    formatted_message = "\n".join(message_parts)
    
    return ComparisonResponse(
        stock1=StockData(**stock1_data),
        stock2=StockData(**stock2_data),
        formatted_message=formatted_message
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
