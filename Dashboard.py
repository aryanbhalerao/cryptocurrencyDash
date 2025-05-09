import streamlit as st
import pandas as pd
import plotly.express as px
from pycoingecko import CoinGeckoAPI

# Set the page layout to wide to minimize gaps on the sides.
st.set_page_config(layout="wide")

# Title and small description for the dashboard
st.title("Cryptocurrency Dashboard")
st.write("Enter the amount of each cryptocurrency you own below:")

# Define the cryptocurrencies with display names and their CoinGecko IDs.
coins = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "Ripple": "ripple",
    "Litecoin": "litecoin",
    "Dogecoin": "dogecoin",
    "Cardano": "cardano",
    "Polkadot": "polkadot",
    "Chainlink": "chainlink",
    "Binance Coin": "binancecoin",
    "Solana": "solana",
    "Stellar": "stellar",
    "VeChain": "vechain",
}

# Create a dictionary to store the user's holdings.
user_holdings = {}

# Arrange input fields with 3 per row:
coin_items = list(coins.items())
for i in range(0, len(coin_items), 3):
    cols = st.columns(3)
    for j, col in enumerate(cols):
        if i + j < len(coin_items):
            display_name, coin_id = coin_items[i + j]
            with col:
                user_holdings[coin_id] = st.number_input(f"{display_name} amount", value=0.0, step=0.01)

# When the "Analyze Portfolio" button is pressed, fetch live data and perform the analysis.
if st.button("Analyze Investment"):
    cg = CoinGeckoAPI()  # Initialize the CoinGecko API wrapper

    coin_ids = ",".join(coins.values())
    try:
        prices = cg.get_price(ids=coin_ids, vs_currencies="usd")
    except Exception as e:
        st.error("Error fetching current prices from CoinGecko. Please try again later.")
        st.error(str(e))
        prices = {}

    # Process the data
    data = []
    total_value = 0.0
    for display_name, coin_id in coins.items():
        amount = user_holdings.get(coin_id, 0)
        coin_data = prices.get(coin_id, {})
        price = coin_data.get("usd", 0)
        value = price * amount
        total_value += value
        data.append({
            "Cryptocurrency": display_name,
            "Amount": amount,
            "Price (USD)": price,
            "Value (USD)": value
        })

    df = pd.DataFrame(data)
    st.subheader(f"Total Portfolio Value: ${total_value:,.2f}")
    st.write("### Detailed Analysis")
    st.dataframe(df)

    # Visualization of portfolio distribution (Bar Chart and Pie Chart)
    chart_data = df[df["Value (USD)"] > 0]  # Filter out zero holdings
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.write("### Portfolio Distribution (Bar Chart)")
        bar_fig = px.bar(
            chart_data,
            x="Cryptocurrency",
            y="Value (USD)",
            hover_data=["Amount", "Price (USD)"]
        )
        bar_fig.update_traces(textposition="none")
        bar_fig.update_layout(showlegend=False)
        st.plotly_chart(bar_fig, use_container_width=True)

    with col_chart2:
        st.write("### Portfolio Distribution (Pie Chart)")
        pie_fig = px.pie(
            chart_data,
            names="Cryptocurrency",
            values="Value (USD)",
            hover_data=["Amount", "Price (USD)"],
            hole=0.3
        )
        pie_fig.update_traces(textinfo="none")
        st.plotly_chart(pie_fig, use_container_width=True)

    # 30-Day Trend Data (Daily Average)
    st.write("### 30-Day Price Trends (Daily Average)")
    trend_series = {}

    for display_name, coin_id in coins.items():
        amount = user_holdings.get(coin_id, 0)
        if amount > 0:
            try:
                trend_json = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency="usd", days=30)
            except Exception as e:
                st.error(f"Error fetching trend data for {display_name}: {str(e)}")
                continue
            prices_list = trend_json.get("prices", [])
            if prices_list:
                # Convert timestamps and aggregate daily prices
                dates = [pd.to_datetime(item[0], unit="ms").date() for item in prices_list]
                prices_only = [item[1] for item in prices_list]
                series = pd.Series(prices_only, index=dates)
                daily_series = series.groupby(series.index).mean()
                trend_series[display_name] = daily_series

    if trend_series:
        df_trends = pd.DataFrame(trend_series)
        df_trends.sort_index(inplace=True)
        trend_fig = px.line(df_trends, labels={"value": "Price (USD)", "index": "Date"})
        trend_fig.update_traces(mode="lines+markers", hovertemplate=None)
        trend_fig.update_layout(showlegend=True)
        st.plotly_chart(trend_fig, use_container_width=True)
    else:
        st.write("No trend data available. Please enter non-zero holdings for at least one cryptocurrency.")
