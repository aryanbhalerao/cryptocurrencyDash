import streamlit as st
import pandas as pd
import plotly.express as px
from pycoingecko import CoinGeckoAPI

# Set page config
st.set_page_config(page_title="Crypto Search", layout="wide")

st.title("Crypto Search")

# Create a CoinGecko API instance
cg = CoinGeckoAPI()

# Helper to get coin list using pycoingecko
@st.cache_data
def get_coin_list():
    return cg.get_coins_list()

# Helper to get coin data (with market information)
def get_coin_data(coin_id):
    return cg.get_coin_by_id(
        id=coin_id,
        localization=False,
        tickers=False,
        market_data=True,
        community_data=False,
        developer_data=False,
        sparkline=False
    )

# Helper to get market chart data (historical price trends)
def get_price_trend(coin_id, days=30):
    return cg.get_coin_market_chart_by_id(id=coin_id, vs_currency="usd", days=days)

# Load coin list and create a mapping for names and IDs.
coins = get_coin_list()
coin_names = {coin["name"]: coin["id"] for coin in coins}
coin_options = ["Select a Cryptocurrency"] + sorted(coin_names.keys())

# Select box for choosing a cryptocurrency.
selected_coin_name = st.selectbox("Choose a Cryptocurrency", coin_options)

if selected_coin_name != "Select a Cryptocurrency":
    coin_id = coin_names[selected_coin_name]

    # Get and display coin statistics.
    with st.spinner("Fetching data..."):
        data = get_coin_data(coin_id)
        market_data = data.get("market_data", {})

        if market_data:
            st.subheader(f" {selected_coin_name} ")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Current Price (USD)", f"${market_data['current_price']['usd']:,}")
            col2.metric("24h Volume", f"${market_data['total_volume']['usd']:,}")
            col3.metric("Market Cap", f"${market_data['market_cap']['usd']:,}")
            col4.metric("Rank", data.get("market_cap_rank", "N/A"))
            col5.metric("Symbol", data.get("symbol", "").upper())

    # Historical price graph using Plotly
    st.subheader("📉 Price Trend (Last 30 Days)")
    price_data = get_price_trend(coin_id)
    prices = price_data.get("prices", [])
    
    if prices:
        df = pd.DataFrame(prices, columns=["Timestamp", "Price"])
        df["Date"] = pd.to_datetime(df["Timestamp"], unit="ms")
        df.set_index("Date", inplace=True)
        
        # Create a Plotly line chart
        fig = px.line(
            df,
            x=df.index,
            y="Price",
            title=f"{selected_coin_name} Price Over Last 30 Days",
            labels={"Price": "Price (USD)", "Date": "Date"}
        )
        fig.update_layout(xaxis_title="Date", yaxis_title="Price (USD)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No price data available.")
else:
    st.info("Please select a cryptocurrency from the dropdown.")
