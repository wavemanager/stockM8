from datetime import datetime, timedelta
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

def get_historical_data(data_client, symbol: str, days_back: int = 100):
    """Holt historische Kursdaten für ein Symbol."""
    try:
        # Use dates that are at least 15 minutes old for paper trading
        end_date = datetime.now() - timedelta(days=1)  # Yesterday
        start_date = end_date - timedelta(days=days_back)
        
        request_params = StockBarsRequest(
            symbol_or_symbols=[symbol],
            timeframe=TimeFrame.Day,
            start=start_date,
            end=end_date
        )

        bars = data_client.get_stock_bars(request_params)
        df = bars.df
        
        if df.empty:
            return None
            
        return df.reset_index(level=0, drop=True)
    except Exception as e:
        print(f"Fehler beim Datenabruf: {e}")
        return None