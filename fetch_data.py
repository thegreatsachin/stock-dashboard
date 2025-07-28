import yfinance as yf
import pandas as pd

def get_stock_data(ticker: str, period='1mo', interval='1d') -> pd.DataFrame:
    """
    Fetches historical stock data for the given ticker and adds technical indicators:
    SMA, EMA, RSI, MACD, and Bollinger Bands.

    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')
        period (str): Data period (e.g., '1mo', '1y')
        interval (str): Data interval (e.g., '1d', '1h')

    Returns:
        pd.DataFrame: Stock data DataFrame with technical indicator columns
    """
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)

    if not df.empty:
        # Simple Moving Average
        df["SMA_20"] = df["Close"].rolling(window=20).mean()

        # Bollinger Bands
        df["STDDEV_20"] = df["Close"].rolling(window=20).std()
        df["Upper_Band"] = df["SMA_20"] + (2 * df["STDDEV_20"])
        df["Lower_Band"] = df["SMA_20"] - (2 * df["STDDEV_20"])

        # Exponential Moving Average
        df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()

        # RSI (14-day)
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df["RSI_14"] = 100 - (100 / (1 + rs))

        # MACD and Signal Line
        ema_12 = df["Close"].ewm(span=12, adjust=False).mean()
        ema_26 = df["Close"].ewm(span=26, adjust=False).mean()
        df["MACD"] = ema_12 - ema_26
        df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    return df
