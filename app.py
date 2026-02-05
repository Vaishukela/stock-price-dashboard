import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Stock Dashboard", layout="wide")

st.title("📈 Stock Price Dashboard")
st.write("Simple finance dashboard to explore stock prices, returns, and volume.")

tickers = st.sidebar.text_input("Enter ticker symbols (comma separated)", "AAPL,MSFT")
tickers = [t.strip().upper() for t in tickers.split(",") if t.strip()]

period = st.sidebar.selectbox(
    "Select time period",
    ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=3
)

if len(tickers) == 0:
    st.warning("Please enter at least one ticker.")
    st.stop()

# Key fix: group_by="ticker" for multiple tickers
data = yf.download(tickers, period=period, auto_adjust=True, group_by="ticker")

def build_df(ticker):
    if len(tickers) == 1:
        df = data.copy().reset_index()
    else:
        df = data[ticker].reset_index()
    df["Ticker"] = ticker
    return df[["Date", "Close", "Volume", "Ticker"]]

df_all = pd.concat([build_df(t) for t in tickers], ignore_index=True).dropna()

st.subheader("Key metrics")

col1, col2, col3 = st.columns(3)
latest_price = df_all.sort_values("Date").groupby("Ticker").tail(1)
avg_price = df_all.groupby("Ticker")["Close"].mean().mean()

col1.metric("Selected stocks", len(tickers))
col2.metric("Latest price (average)", f"{latest_price['Close'].mean():.2f}")
col3.metric("Average price", f"{avg_price:.2f}")

st.subheader("Price trend")
fig_price = px.line(df_all, x="Date", y="Close", color="Ticker", title="Stock price over time")
st.plotly_chart(fig_price, use_container_width=True)

df_all["Daily return (%)"] = df_all.groupby("Ticker")["Close"].pct_change() * 100

st.subheader("Daily returns")
fig_ret = px.line(df_all.dropna(), x="Date", y="Daily return (%)", color="Ticker", title="Daily returns")
st.plotly_chart(fig_ret, use_container_width=True)

st.subheader("Trading volume")
fig_vol = px.bar(df_all, x="Date", y="Volume", color="Ticker", title="Trading volume")
st.plotly_chart(fig_vol, use_container_width=True)
