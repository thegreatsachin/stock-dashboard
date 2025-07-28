import yfinance as yf
import pandas as pd

def get_stock_data(ticker: str, period='1mo', interval='1d') -> pd.DataFrame:
    """
    Fetches historical stock data for the given ticker and adds SMA and EMA indicators.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')
        period (str): Data period (e.g., '1mo', '1y')
        interval (str): Data interval (e.g., '1d', '1h')

    Returns:
        pd.DataFrame: Stock data DataFrame with SMA and EMA columns
    """
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)

    if not df.empty:
        df["SMA_20"] = df["Close"].rolling(window=20).mean()
        df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()

    return df
