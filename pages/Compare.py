import streamlit as st
import pandas as pd
import plotly.express as px
from pycoingecko import CoinGeckoAPI

# Configure the page layout and title
st.set_page_config(page_title="Cryptocurrency Comparison", layout="wide")
st.title("Compare Cryptocurrencies")

# Initialize the CoinGecko API instance
cg = CoinGeckoAPI()

@st.cache_data
def get_top_coins():
    return cg.get_coins_markets(
        vs_currency="usd",
        order="market_cap_desc",
        per_page=50,
        page=1,
        sparkline=False
    )

# Retrieve top coins and build mapping
top_coins = get_top_coins()
coin_options = {coin["name"]: coin["id"] for coin in top_coins}
sorted_names = sorted(coin_options.keys())

# Selection boxes (no default)
col_select1, col_select2 = st.columns(2)
with col_select1:
    coin1_name = st.selectbox("🔹 Select the first cryptocurrency", [""] + sorted_names)
with col_select2:
    coin2_name = st.selectbox("🔸 Select the second cryptocurrency", [""] + sorted_names)

if coin1_name and coin2_name and coin1_name != coin2_name:
    coin1_id = coin_options[coin1_name]
    coin2_id = coin_options[coin2_name]

    coin1_data = cg.get_coin_by_id(id=coin1_id, localization=False, tickers=False, market_data=True)
    coin2_data = cg.get_coin_by_id(id=coin2_id, localization=False, tickers=False, market_data=True)

    coin1_price = coin1_data.get("market_data", {}).get("current_price", {}).get("usd")
    coin2_price = coin2_data.get("market_data", {}).get("current_price", {}).get("usd")

    if coin1_price is None or coin2_price is None:
        st.error("❌ Could not retrieve pricing data.")
    else:
        # Side-by-side stats
        st.markdown("## Cryptocurrency Statistics")
        col_stat1, col_stat2 = st.columns(2)

        def render_stats(col, coin_name, coin_data, price):
            market_data = coin_data.get("market_data", {})
            market_cap = market_data.get("market_cap", {}).get("usd")
            volume = market_data.get("total_volume", {}).get("usd")
            symbol = coin_data.get("symbol", "").upper()
            rank = coin_data.get("market_cap_rank", "N/A")

            with col:
                st.markdown(f"### {coin_name}")
                st.metric("Current Price (USD)", f"${price:,.2f}")
                st.write(f"**Symbol:** `{symbol}`")
                st.write(f"**Market Cap:** {'${:,.0f}'.format(market_cap) if market_cap else 'N/A'}")
                st.write(f"**24h Volume:** {'${:,.0f}'.format(volume) if volume else 'N/A'}")
                st.write(f"**Market Rank:** {rank}")

        render_stats(col_stat1, coin1_name, coin1_data, coin1_price)
        render_stats(col_stat2, coin2_name, coin2_data, coin2_price)

        # Historical trend
        st.markdown("## 📈 Price Trends")
        try:
            trend_days = 30
            trend_data1 = cg.get_coin_market_chart_by_id(id=coin1_id, vs_currency="usd", days=trend_days)
            trend_data2 = cg.get_coin_market_chart_by_id(id=coin2_id, vs_currency="usd", days=trend_days)

            df1 = pd.DataFrame(trend_data1.get("prices", []), columns=["Timestamp", coin1_name])
            df2 = pd.DataFrame(trend_data2.get("prices", []), columns=["Timestamp", coin2_name])
            df1["Timestamp"] = pd.to_datetime(df1["Timestamp"], unit="ms")
            df2["Timestamp"] = pd.to_datetime(df2["Timestamp"], unit="ms")

            fig = px.line(title="30-Day Price Trend Comparison")
            fig.add_scatter(x=df1["Timestamp"], y=df1[coin1_name], mode="lines", name=coin1_name)
            fig.add_scatter(x=df2["Timestamp"], y=df2[coin2_name], mode="lines", name=coin2_name)

            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ Error fetching historical data: {e}")
elif coin1_name and coin2_name and coin1_name == coin2_name:
    st.warning("⚠️ Please select **two different cryptocurrencies**.")
else:
    st.info("ℹ️ Select two cryptocurrencies above to compare.")

