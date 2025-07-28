import streamlit as st
from fetch_data import get_stock_data
import plotly.graph_objs as go

# Streamlit UI
st.set_page_config(page_title="Real-Time Stock Dashboard", layout="wide")
st.title("📈 Real-Time Stock Market Dashboard")

# Sidebar
st.sidebar.header("Select Options")
ticker = st.sidebar.text_input("Stock Ticker Symbol", value="AAPL", max_chars=10)
period = st.sidebar.selectbox("Select Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y"])
interval = st.sidebar.selectbox("Data Interval", ["1m", "5m", "15m", "30m", "1h", "1d"])

# Fetch Data
df = get_stock_data(ticker, period=period, interval=interval)

if not df.empty:
    st.subheader(f"{ticker.upper()} Stock Price")
    
    # Plot with Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close Price"))
    fig.update_layout(title=f"{ticker.upper()} Price Over Time", xaxis_title="Time", yaxis_title="Price (USD)")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df.tail(10))
else:
    st.error("No data found. Please check the ticker or try another time range.")
