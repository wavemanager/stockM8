import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus

# --- 1. Loads the API-Keys out of the .env file ---
# Make sure you have a .env file in the same folder with:
load_dotenv()

# --- 2. Initialize the Trading Client ---
# The client automatically reads the keys from the environment variables.
# paper=True is crucial to connect to your paper trading account.
trading_client = TradingClient(
    os.getenv("APCA_API_KEY_ID"),
    os.getenv("APCA_API_SECRET_KEY"),
    paper=True
)

print("✅ Successfully connected to the Alpaca Paper Trading account.")

# --- 3. Request Account Information ---
try:
    # get_account() retrieves an object with all important account data.
    account = trading_client.get_account()

    # We output the equity. This is the total value of your account.
    # You could also query other values like 'cash' or 'portfolio_value'.
    print(f"\n--- My Account Balance ---")
    print(f"Current Equity: ${account.equity}")
    print(f"Available Cash: ${account.cash}")

except Exception as e:
    print(f"Error retrieving account information: {e}")


# (Dein bisheriger Code zum Verbinden und Abfragen bleibt oben)
# ...

from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# --- 5. Eine Market-Order basierend auf Benutzereingabe platzieren ---
try:
    print("\n--- Platziere eine neue Order ---")

    # NEU: Frage den Benutzer, welche Aktie gekauft werden soll.
    # .upper() wandelt die Eingabe direkt in Großbuchstaben um (z.B. 'aapl' -> 'AAPL')
    symbol_input = input("Welches Aktiensymbol möchtest du kaufen? (z.B. GOOG, TSLA): ").upper()

    # Überprüfe, ob eine Eingabe gemacht wurde
    if not symbol_input:
        print("Kein Symbol eingegeben. Breche den Vorgang ab.")
    else:
        # Vorbereitung der Order-Daten mit der Benutzereingabe
        market_order_data = MarketOrderRequest(
            symbol=symbol_input,      # Hier wird die Eingabe verwendet
            qty=1,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )

        # Order an die Alpaca API senden
        print(f"Sende Kauf-Order für 1x {symbol_input}...")
        market_order = trading_client.submit_order(
            order_data=market_order_data
        )

        print("🚀 Order erfolgreich platziert!")
        # Jede Order hat eine einzigartige ID, die du zur Verfolgung nutzen kannst
        print(f"Order ID: {market_order.id} | Symbol: {market_order.symbol} | Status: {market_order.status.value}")

except Exception as e:
    print(f"Fehler beim Platzieren der Order: {e}")
