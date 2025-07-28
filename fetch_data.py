import yfinance as yf
import pandas as pd

def get_stock_data(ticker: str, period='1mo', interval='1d') -> pd.DataFrame:
    """
    Fetches historical stock data for the given ticker.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')
        period (str): Data period (e.g., '1mo', '1y')
        interval (str): Data interval (e.g., '1d', '1h')

    Returns:
        pd.DataFrame: Stock data DataFrame
    """
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)
    return df
