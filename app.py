import streamlit as st
from fetch_data import get_stock_data
import plotly.graph_objs as go
import pandas as pd

# Streamlit UI setup
st.set_page_config(page_title="Real-Time Stock Dashboard", layout="wide")
st.title("📈 Real-Time Stock Market Dashboard")

# Sidebar options
st.sidebar.header("Select Options")

tickers = st.sidebar.multiselect(
    "Select Stock Tickers (Up to 3)",
    options=["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NFLX"],
    default=["AAPL", "GOOGL"],
)

if len(tickers) == 0:
    st.sidebar.warning("Please select at least one ticker.")

if len(tickers) > 3:
    st.sidebar.error("Please select up to 3 tickers only.")
    tickers = tickers[:3]  # limit to first 3 tickers

period = st.sidebar.selectbox("Select Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y"])
interval = st.sidebar.selectbox("Data Interval", ["1m", "5m", "15m", "30m", "1h", "1d"])

# Indicator options
st.sidebar.subheader("Indicators")
show_sma = st.sidebar.checkbox("Show SMA (20)", value=True)
show_ema = st.sidebar.checkbox("Show EMA (20)", value=True)
show_rsi = st.sidebar.checkbox("Show RSI (14)")
show_macd = st.sidebar.checkbox("Show MACD")
show_bbands = st.sidebar.checkbox("Show Bollinger Bands")  # New checkbox added here

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data, fast=12, slow=26, signal=9):
    ema_fast = data.ewm(span=fast, adjust=False).mean()
    ema_slow = data.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

# --- Multi-Stock Comparison Chart ---
if tickers:
    st.subheader("📊 Multi-Stock Comparison")

    multi_fig = go.Figure()
    for symbol in tickers:
        df_multi = get_stock_data(symbol, period=period, interval=interval)
        if not df_multi.empty:
            multi_fig.add_trace(go.Scatter(x=df_multi.index, y=df_multi["Close"], name=symbol))

    multi_fig.update_layout(
        title="Closing Price Comparison",
        xaxis_title="Time",
        yaxis_title="Price (USD)"
    )
    st.plotly_chart(multi_fig, use_container_width=True)

if tickers:
    # Fetch data for all tickers and combine closing prices into one DataFrame
    close_prices = pd.DataFrame()

    dfs = {}  # store each ticker's dataframe for indicators (optional)
    for t in tickers:
        df = get_stock_data(t, period=period, interval=interval)
        if not df.empty:
            dfs[t] = df
            close_prices[t] = df["Close"]
        else:
            st.warning(f"No data found for {t}")

    if not close_prices.empty:
        # Optionally, show indicators for each ticker (for now, just first ticker selected)
        first_ticker = tickers[0]
        df = dfs[first_ticker]

        if not df.empty:
            # Calculate indicators for the first ticker only (to avoid clutter)
            if show_sma:
                df["SMA_20"] = df["Close"].rolling(window=20).mean()
            if show_bbands:
                df["STDDEV_20"] = df["Close"].rolling(window=20).std()
                df["Upper_Band"] = df["SMA_20"] + (2 * df["STDDEV_20"])
                df["Lower_Band"] = df["SMA_20"] - (2 * df["STDDEV_20"])
            if show_ema:
                df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
            if show_rsi:
                df["RSI_14"] = calculate_rsi(df["Close"], 14)
            if show_macd:
                df["MACD"], df["Signal"], df["MACD_hist"] = calculate_macd(df["Close"])

            st.subheader(f"{first_ticker.upper()} Indicators")

            fig_ind = go.Figure()
            fig_ind.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close Price"))

            if show_sma:
                fig_ind.add_trace(go.Scatter(x=df.index, y=df["SMA_20"], mode="lines", name="SMA (20)"))

            if show_bbands and all(x in df.columns for x in ["Upper_Band", "Lower_Band"]):
                fig_ind.add_trace(go.Scatter(
                    x=df.index,
                    y=df["Upper_Band"],
                    mode="lines",
                    name="Upper Band",
                    line=dict(color="grey", dash='dash')
                ))
                fig_ind.add_trace(go.Scatter(
                    x=df.index,
                    y=df["Lower_Band"],
                    mode="lines",
                    name="Lower Band",
                    line=dict(color="grey", dash='dash')
                ))

            if show_ema:
                fig_ind.add_trace(go.Scatter(x=df.index, y=df["EMA_20"], mode="lines", name="EMA (20)"))

            fig_ind.update_layout(
                title=f"{first_ticker.upper()} Price with Indicators",
                xaxis_title="Time",
                yaxis_title="Price (USD)",
                legend_title="Legend"
            )
            st.plotly_chart(fig_ind, use_container_width=True)

            # RSI Plot
            if show_rsi and "RSI_14" in df.columns:
                st.subheader("RSI (14)")
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=df.index, y=df["RSI_14"], name="RSI", line=dict(color="orange")))
                fig_rsi.update_layout(yaxis=dict(range=[0, 100]), xaxis_title="Date", yaxis_title="RSI")
                st.plotly_chart(fig_rsi, use_container_width=True)

            # MACD Plot
            if show_macd and "MACD" in df.columns:
                st.subheader("MACD")
                fig_macd = go.Figure()
                fig_macd.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD", line=dict(color="blue")))
                fig_macd.add_trace(go.Scatter(x=df.index, y=df["Signal"], name="Signal", line=dict(color="red")))
                st.plotly_chart(fig_macd, use_container_width=True)

            # Display last few rows of data
            st.dataframe(df.tail(10))

            # CSV Download Button for first ticker
            csv = df.to_csv().encode('utf-8')
            st.download_button(
                label=f"📥 Download {first_ticker.upper()} CSV",
                data=csv,
                file_name=f"{first_ticker}_data.csv",
                mime='text/csv'
            )
    else:
        st.error("No valid data available for selected tickers.")

else:
    st.info("Select at least one ticker to see data.")
