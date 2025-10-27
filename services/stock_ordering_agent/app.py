"""
Stock Ordering Agent - Einfache Version für Anfänger
====================================================

Was macht dieser Agent?
- Platziert Kauf/Verkauf Orders bei Alpaca (Paper Trading)
- Checkt ob die Börse offen ist
- Gibt formatierte Nachrichten zurück

Endpoints:
- GET  /               → Status-Check
- GET  /market-status  → Ist die Börse offen?
- POST /order/market   → Kaufe/Verkaufe zum aktuellen Preis
- POST /order/limit    → Kaufe/Verkaufe nur zu bestimmtem Preis
"""

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# ============================================================================
# SCHRITT 1: Umgebung einrichten
# ============================================================================

# Lade API Keys aus .env Datei (2 Ordner höher)
dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path=dotenv_path)

# Erstelle FastAPI App
app = FastAPI(title="Stock Ordering Agent")

# Verbinde mit Alpaca Paper Trading Account
trading_client = TradingClient(
    api_key=os.getenv("APCA_API_KEY_ID"),      # Dein API Key
    secret_key=os.getenv("APCA_API_SECRET_KEY"),  # Dein Secret Key
    paper=True  # WICHTIG: Paper Trading = virtuelles Geld!
)

print("✅ Verbindung zu Alpaca Paper Trading hergestellt!")


# ============================================================================
# SCHRITT 2: Datenmodelle definieren (Was kann man senden/empfangen?)
# ============================================================================

class MarketOrderInput(BaseModel):
    """Was der User schickt für eine Market Order"""
    symbol: str        # z.B. "AAPL", "TSLA"
    qty: int = 1       # Anzahl Aktien (Standard: 1)
    side: str = "buy"  # "buy" oder "sell"

class LimitOrderInput(BaseModel):
    """Was der User schickt für eine Limit Order"""
    symbol: str
    qty: int = 1
    side: str = "buy"
    limit_price: float  # Preis bei dem gekauft/verkauft werden soll

class OrderResponse(BaseModel):
    """Was der Agent zurückgibt"""
    order_id: str           # Eindeutige Order ID
    symbol: str             # Aktien-Symbol
    qty: int                # Anzahl
    side: str               # "buy" oder "sell"
    status: str             # "accepted", "filled", etc.
    order_type: str         # "market" oder "limit"
    formatted_message: str  # Schöne Nachricht für User


# ============================================================================
# SCHRITT 3: Hilfsfunktionen
# ============================================================================

def check_market_status():
    """
    Prüft ob die Börse geöffnet ist
    
    Returns:
        tuple: (is_open: bool, warning_message: str)
    """
    try:
        clock = trading_client.get_clock()
        
        if not clock.is_open:
            warning = f"\n⚠️ Börse ist GESCHLOSSEN\n⏰ Öffnet wieder: {clock.next_open}\n📝 Order wird bei Öffnung ausgeführt\n"
            return False, warning
        else:
            return True, ""
    except:
        return True, ""  # Falls Check fehlschlägt, trotzdem Order erlauben


def format_market_order_message(result, side, market_warning=""):
    """
    Erstellt schöne formatierte Nachricht für Market Order
    
    Args:
        result: Order-Objekt von Alpaca
        side: OrderSide.BUY oder OrderSide.SELL
        market_warning: Optional Warnung wenn Markt geschlossen
    
    Returns:
        str: Formatierte Nachricht
    """
    action = "KAUFEN" if side == OrderSide.BUY else "VERKAUFEN"
    emoji = "🟢" if side == OrderSide.BUY else "🔴"
    
    message = f"""{emoji} ORDER PLATZIERT

📝 Order-Art: MARKET {action}
🏷️ Aktie: {result.symbol}
📊 Anzahl: {result.qty} Stück
⏰ Status: {result.status.value}
🆔 Order-ID: {result.id}
{market_warning}
💰 Wird zum aktuellen Marktpreis ausgeführt
⌛ Gültig bis: Ausführung oder Stornierung

🤖 Powered by StockM8"""
    
    return message


def format_limit_order_message(result, side, limit_price, market_warning=""):
    """
    Erstellt schöne formatierte Nachricht für Limit Order
    
    Args:
        result: Order-Objekt von Alpaca
        side: OrderSide.BUY oder OrderSide.SELL
        limit_price: Gewünschter Preis
        market_warning: Optional Warnung wenn Markt geschlossen
    
    Returns:
        str: Formatierte Nachricht
    """
    action = "KAUFEN" if side == OrderSide.BUY else "VERKAUFEN"
    emoji = "🟢" if side == OrderSide.BUY else "🔴"
    condition = "bei oder unter" if side == OrderSide.BUY else "bei oder über"
    
    message = f"""{emoji} LIMIT ORDER PLATZIERT

📝 Order-Art: LIMIT {action}
🏷️ Aktie: {result.symbol}
📊 Anzahl: {result.qty} Stück
💵 Limit-Preis: ${limit_price}
⏰ Status: {result.status.value}
🆔 Order-ID: {result.id}
{market_warning}
⚡ Wird nur ausgeführt {condition} ${limit_price}
⌛ Gültig bis: Ausführung oder Stornierung

🤖 Powered by StockM8"""
    
    return message


# ============================================================================
# SCHRITT 4: API Endpoints
# ============================================================================

@app.get("/")
def root():
    """
    Haupt-Endpoint: Zeigt Status und ob Börse offen ist
    
    Beispiel:
        curl http://localhost:80/
    """
    try:
        clock = trading_client.get_clock()
        return {
            "status": "Stock Ordering Agent läuft",
            "market_open": clock.is_open,
            "next_open": str(clock.next_open) if not clock.is_open else None,
            "next_close": str(clock.next_close) if clock.is_open else None,
            "endpoints": ["/market-status", "/order/market", "/order/limit"]
        }
    except:
        return {
            "status": "Stock Ordering Agent läuft",
            "endpoints": ["/market-status", "/order/market", "/order/limit"]
        }


@app.get("/market-status")
def market_status():
    """
    Detaillierter Börsen-Status
    
    Beispiel:
        curl http://localhost:80/market-status
    
    Returns:
        dict: Status mit formatierter Nachricht
    """
    try:
        clock = trading_client.get_clock()
        
        status_emoji = "🟢" if clock.is_open else "🔴"
        status_text = "OFFEN" if clock.is_open else "GESCHLOSSEN"
        
        message = f"""{status_emoji} BÖRSEN-STATUS

📊 Börse ist: {status_text}
🕐 Aktuelle Zeit: {clock.timestamp}

"""
        
        if clock.is_open:
            message += f"⏰ Schließt um: {clock.next_close}\n"
        else:
            message += f"⏰ Öffnet wieder: {clock.next_open}\n"
        
        message += "\n🤖 Powered by StockM8"
        
        return {
            "is_open": clock.is_open,
            "timestamp": str(clock.timestamp),
            "next_open": str(clock.next_open),
            "next_close": str(clock.next_close),
            "formatted_message": message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Status-Check: {str(e)}")


@app.post("/order/market", response_model=OrderResponse)
def place_market_order(order: MarketOrderInput):
    """
    Platziert eine Market Order (sofort zum aktuellen Preis)
    
    Beispiel:
        curl -X POST http://localhost:80/order/market \\
          -H "Content-Type: application/json" \\
          -d '{"symbol": "AAPL", "qty": 1, "side": "buy"}'
    
    Args:
        order: MarketOrderInput mit symbol, qty, side
    
    Returns:
        OrderResponse: Details der platzierten Order
    """
    try:
        # 1. Check ob Börse offen ist
        is_open, market_warning = check_market_status()
        
        # 2. Bestimme Kauf oder Verkauf
        side = OrderSide.BUY if order.side.lower() == "buy" else OrderSide.SELL
        
        # 3. Erstelle Order-Request für Alpaca
        market_order_data = MarketOrderRequest(
            symbol=order.symbol.upper(),  # Großbuchstaben (AAPL, TSLA)
            qty=order.qty,                # Anzahl Aktien
            side=side,                    # BUY oder SELL
            time_in_force=TimeInForce.GTC # Good-Till-Canceled (bleibt bis ausgeführt)
        )
        
        # 4. Sende Order an Alpaca
        result = trading_client.submit_order(order_data=market_order_data)
        
        # 5. Erstelle schöne Nachricht
        formatted_msg = format_market_order_message(result, side, market_warning)
        
        # 6. Gib Antwort zurück
        return OrderResponse(
            order_id=str(result.id),
            symbol=result.symbol,
            qty=int(result.qty),
            side=result.side.value,
            status=result.status.value,
            order_type="market",
            formatted_message=formatted_msg
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Platzieren der Order: {str(e)}")


@app.post("/order/limit", response_model=OrderResponse)
def place_limit_order(order: LimitOrderInput):
    """
    Platziert eine Limit Order (nur zu bestimmtem Preis oder besser)
    
    Beispiel:
        curl -X POST http://localhost:80/order/limit \\
          -H "Content-Type: application/json" \\
          -d '{"symbol": "TSLA", "qty": 1, "side": "buy", "limit_price": 240.00}'
    
    Args:
        order: LimitOrderInput mit symbol, qty, side, limit_price
    
    Returns:
        OrderResponse: Details der platzierten Order
    """
    try:
        # 1. Check ob Börse offen ist
        is_open, market_warning = check_market_status()
        
        # 2. Bestimme Kauf oder Verkauf
        side = OrderSide.BUY if order.side.lower() == "buy" else OrderSide.SELL
        
        # 3. Erstelle Order-Request für Alpaca
        limit_order_data = LimitOrderRequest(
            symbol=order.symbol.upper(),
            qty=order.qty,
            side=side,
            limit_price=order.limit_price,  # Gewünschter Preis
            time_in_force=TimeInForce.GTC
        )
        
        # 4. Sende Order an Alpaca
        result = trading_client.submit_order(order_data=limit_order_data)
        
        # 5. Erstelle schöne Nachricht
        formatted_msg = format_limit_order_message(result, side, order.limit_price, market_warning)
        
        # 6. Gib Antwort zurück
        return OrderResponse(
            order_id=str(result.id),
            symbol=result.symbol,
            qty=int(result.qty),
            side=result.side.value,
            status=result.status.value,
            order_type="limit",
            formatted_message=formatted_msg
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Platzieren der Order: {str(e)}")


# ============================================================================
# SCHRITT 5: Server starten (nur für lokale Tests)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Stock Ordering Agent startet...")
    print("="*60)
    print("\n📍 Server läuft auf: http://localhost:80")
    print("📚 API Docs: http://localhost:80/docs")
    print("\n💡 Beispiel-Befehle:")
    print("\n1. Status checken:")
    print("   curl http://localhost:80/market-status")
    print("\n2. Aktie kaufen:")
    print('   curl -X POST http://localhost:80/order/market \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"symbol": "AAPL", "qty": 1, "side": "buy"}\'')
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=80)
