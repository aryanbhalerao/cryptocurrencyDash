import streamlit as st
import pandas as pd
import plotly.express as px
from pycoingecko import CoinGeckoAPI
from sklearn.linear_model import LinearRegression
import numpy as np

# Initialize API
cg = CoinGeckoAPI()

# Streamlit UI
st.title("Future Trend Prediction using AI")

# User Input
crypto = st.text_input("Enter Cryptocurrency: ", "bitcoin")

# Fetch Last Month Data
data = cg.get_coin_market_chart_by_id(id=crypto, vs_currency='usd', days=30)
df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df['days'] = np.arange(len(df))

# Current Price
current_price = df['price'].iloc[-1]

# Train Linear Regression Model
X = df[['days']]
y = df['price']

model = LinearRegression()
model.fit(X, y)
df['predicted_price'] = model.predict(X)

# Predict Next Month's Price
future_days = np.arange(len(df), len(df) + 30).reshape(-1, 1)
future_prices = model.predict(future_days)
future_df = pd.DataFrame({'days': future_days.flatten(), 'price': future_prices})
future_df['timestamp'] = df['timestamp'].iloc[-1] + pd.to_timedelta(future_df['days'] - df['days'].iloc[-1], unit='D')

# Future Price Prediction (last day's prediction of next month)
predicted_next_month_price = future_df['price'].iloc[-1]

# Display Price Information (above graph)
st.markdown(f"""
    <div style="display: flex; justify-content: space-between; font-size: 24px; font-weight: bold;">
        <span style="color: green;">Current Price: ${current_price:.2f}</span>
        <span style="color: red;">Predicted Price (Next Month): ${predicted_next_month_price:.2f}</span>
    </div>
""", unsafe_allow_html=True)

# Plot Graph
fig = px.line(df, x='timestamp', y=['price', 'predicted_price'], title=f"{crypto.capitalize()} Price Trend")
fig.add_scatter(x=future_df['timestamp'], y=future_df['price'], mode='lines', name='Next Month Prediction')

st.plotly_chart(fig)

st.write("This tool uses Linear Regression for trend estimation.")
