from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import OrderSide, QueryOrderStatus
import os
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path=dotenv_path)

app = FastAPI(title="Alpaca Account Info Agent")

# Initialize Alpaca Trading Client
trading_client = TradingClient(
    api_key=os.getenv('APCA_API_KEY_ID'),
    secret_key=os.getenv('APCA_API_SECRET_KEY'),
    paper=True  # Paper trading
)

class AccountInfoResponse(BaseModel):
    formatted_message: str
    account_value: float
    buying_power: float
    cash: float
    portfolio_value: float
    positions_count: int
    open_orders_count: int

@app.get("/")
def read_root():
    return {"status": "Alpaca Account Agent is running", "endpoints": ["/account-info"]}

@app.get("/account-info", response_model=AccountInfoResponse)
def get_account_info():
    """
    Returns comprehensive account information including:
    - Account balance, buying power, cash
    - Current positions
    - Open orders
    - Formatted message ready for Telegram
    """
    try:
        # Get account details
        account = trading_client.get_account()
        
        # Get all positions
        positions = trading_client.get_all_positions()
        
        # Get open orders
        order_request = GetOrdersRequest(
            status=QueryOrderStatus.OPEN
        )
        open_orders = trading_client.get_orders(filter=order_request)
        
        # Build formatted message
        message_parts = []
        
        # Header
        message_parts.append("💼 YOUR ALPACA ACCOUNT")
        message_parts.append("")
        
        # Account Overview
        message_parts.append("📊 ACCOUNT OVERVIEW")
        message_parts.append("")
        message_parts.append(f"💰 Total Value: ${float(account.portfolio_value):,.2f}")
        message_parts.append(f"💵 Cash: ${float(account.cash):,.2f}")
        message_parts.append(f"⚡ Buying Power: ${float(account.buying_power):,.2f}")
        message_parts.append(f"📈 Equity: ${float(account.equity):,.2f}")
        message_parts.append("")
        
        # Day's Performance
        if account.equity != account.last_equity:
            change = float(account.equity) - float(account.last_equity)
            change_percent = (change / float(account.last_equity)) * 100
            emoji = "🟢" if change >= 0 else "🔴"
            sign = "+" if change >= 0 else ""
            message_parts.append(f"📊 Today: {sign}${change:,.2f} ({sign}{change_percent:.2f}%) {emoji}")
            message_parts.append("")
        
        # Positions
        message_parts.append(f"📦 POSITIONS ({len(positions)})")
        message_parts.append("")
        
        if positions:
            for position in positions:
                symbol = position.symbol
                qty = float(position.qty)
                current_price = float(position.current_price)
                market_value = float(position.market_value)
                unrealized_pl = float(position.unrealized_pl)
                unrealized_plpc = float(position.unrealized_plpc) * 100
                
                pl_emoji = "🟢" if unrealized_pl >= 0 else "🔴"
                pl_sign = "+" if unrealized_pl >= 0 else ""
                
                message_parts.append(f"• {symbol}")
                message_parts.append(f"  {qty} shares @ ${current_price:.2f}")
                message_parts.append(f"  Value: ${market_value:,.2f}")
                message_parts.append(f"  P/L: {pl_sign}${unrealized_pl:,.2f} ({pl_sign}{unrealized_plpc:.2f}%) {pl_emoji}")
                message_parts.append("")
        else:
            message_parts.append("No open positions")
            message_parts.append("")
        
        # Open Orders
        message_parts.append(f"📋 OPEN ORDERS ({len(open_orders)})")
        message_parts.append("")
        
        if open_orders:
            for order in open_orders:
                side_emoji = "🟢" if order.side == OrderSide.BUY else "🔴"
                message_parts.append(f"{side_emoji} {order.side.value} {order.symbol}")
                message_parts.append(f"  {order.qty} shares @ ${float(order.limit_price or 0):.2f}")
                message_parts.append(f"  Status: {order.status.value}")
                message_parts.append("")
        else:
            message_parts.append("No open orders")
            message_parts.append("")
        
        # Footer
        message_parts.append("🤖 Powered by StockM8")
        
        formatted_message = "\n".join(message_parts)
        
        return AccountInfoResponse(
            formatted_message=formatted_message,
            account_value=float(account.portfolio_value),
            buying_power=float(account.buying_power),
            cash=float(account.cash),
            portfolio_value=float(account.portfolio_value),
            positions_count=len(positions),
            open_orders_count=len(open_orders)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching account info: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
