import streamlit as st
import pandas as pd
from pycoingecko import CoinGeckoAPI

# Set page config
st.set_page_config(page_title="Leaderboard", layout="wide")

st.title("Leaderboard")

# Create an instance of CoinGeckoAPI
cg = CoinGeckoAPI()

# Fetch cryptocurrency market data using pycoingecko's get_coins_markets method
def get_crypto_data():
    try:
        data = cg.get_coins_markets(
            vs_currency="usd",
            order="market_cap_desc",
            per_page=25,
            page=1,
            sparkline=False,
        )
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

crypto_data = get_crypto_data()
if crypto_data:
    df = pd.DataFrame(
        crypto_data, columns=["name", "symbol", "current_price", "market_cap", "total_volume"]
    )

    # Add Rank column
    df.insert(0, "Rank", range(1, len(df) + 1))

    # Rename columns to improve readability
    df.rename(
        columns={
            "name": "Name",
            "symbol": "Symbol",
            "current_price": "Price (USD)",
            "market_cap": "Market Cap",
            "total_volume": "24h Volume",
        },
        inplace=True,
    )

    # Display the governance table with st.table() to avoid scrolling
    st.table(df)
else:
    st.error("Failed to fetch data. Please try again later.")
