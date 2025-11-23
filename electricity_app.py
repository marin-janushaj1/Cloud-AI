# electricity_app.py — Final Working Version (Regression Forecasting)

import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import timedelta
import plotly.graph_objects as go


# --------------------------------------------------
# Load trained PyCaret regression model (cached)
# --------------------------------------------------
@st.cache_resource
def load_model_file():
    return joblib.load("models/best_electricity_model_fast.pkl")

model = load_model_file()


# --------------------------------------------------
# Load historical data (cached)
# --------------------------------------------------
@st.cache_data
def load_history():
    df = pd.read_parquet("data/clean/uk_electricity_hourly.parquet")
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    return df

history = load_history()


# --------------------------------------------------
# Feature engineering (MUST match training)
# --------------------------------------------------
TRAIN_FEATURES = [
    "hour", "day_of_week", "month", "week", "is_weekend",
    "lag_1", "lag_24", "lag_168", "roll_24", "roll_168"
]

def add_features(df):
    df["hour"] = df.index.hour
    df["day_of_week"] = df.index.dayofweek
    df["month"] = df.index.month
    df["week"] = df.index.isocalendar().week.astype(int)
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    return df


def make_input_row(ts, hist_df):
    """Construct a 1-row dataframe matching EXACT model features."""

    temp = pd.DataFrame(index=[ts])
    temp = add_features(temp)

    # Lag features using last known true/predicted demand
    temp["lag_1"] = hist_df["demand_mw"].iloc[-1]
    temp["lag_24"] = hist_df["demand_mw"].iloc[-24]
    temp["lag_168"] = hist_df["demand_mw"].iloc[-168]

    # Rolling means
    temp["roll_24"] = hist_df["demand_mw"].iloc[-24:].mean()
    temp["roll_168"] = hist_df["demand_mw"].iloc[-168:].mean()

    # Ensure correct feature set
    for col in TRAIN_FEATURES:
        if col not in temp:
            temp[col] = 0

    temp = temp[TRAIN_FEATURES]   # correct order

    return temp


# --------------------------------------------------
# Recursive multi-step forecasting
# --------------------------------------------------
def forecast_future(horizon_hours):
    df = history.copy()
    last_ts = df.index.max()
    results = []

    for _ in range(horizon_hours):
        next_ts = last_ts + timedelta(hours=1)

        row = make_input_row(next_ts, df)
        yhat = float(model.predict(row)[0])

        # Append forecast to history so lags update
        df.loc[next_ts, "demand_mw"] = yhat
        results.append((next_ts, yhat))

        last_ts = next_ts

    pred_df = pd.DataFrame(results, columns=["timestamp", "forecast"])
    pred_df.set_index("timestamp", inplace=True)
    return pred_df


# --------------------------------------------------
# Streamlit UI
# --------------------------------------------------
st.set_page_config(page_title="Electricity Forecast", page_icon="⚡", layout="wide")

st.title("⚡ UK Electricity Demand Predictor")
st.write("Forecast electricity demand using a PyCaret regression model.")

# Sidebar settings
st.sidebar.header("Forecast Settings")
mode = st.sidebar.radio("Forecast horizon type", ["Hours", "Days", "Weeks"])

if mode == "Hours":
    horizon = st.sidebar.slider("Hours to forecast", 1, 240, 72)
elif mode == "Days":
    horizon = st.sidebar.slider("Days to forecast", 1, 30, 7) * 24
else:
    horizon = st.sidebar.slider("Weeks to forecast", 1, 8, 2) * 7 * 24

show_history = st.sidebar.checkbox("Show history", True)
history_days = st.sidebar.slider("History window (days)", 1, 60, 14) if show_history else 0


# --------------------------------------------------
# Run forecast
# --------------------------------------------------
if st.button("Run Forecast", use_container_width=True):
    pred_df = forecast_future(horizon)

    st.success("Forecast generated successfully!")

    # Plot forecast only
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=pred_df.index, y=pred_df["forecast"],
                             name="Forecast", line=dict(color="cyan", width=3)))
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Plot history + forecast
    if show_history:
        hist = history.tail(history_days * 24)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=hist.index, y=hist["demand_mw"],
                                  name="History", line=dict(color="orange", width=2)))
        fig2.add_trace(go.Scatter(x=pred_df.index, y=pred_df["forecast"],
                                  name="Forecast", line=dict(color="cyan", width=3)))
        fig2.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig2, use_container_width=True)

    # Summary metrics
    st.metric("Min (MW)", f"{pred_df['forecast'].min():,.0f}")
    st.metric("Max (MW)", f"{pred_df['forecast'].max():,.0f}")
    st.metric("Avg (MW)", f"{pred_df['forecast'].mean():,.0f}")

    # Forecast table
    st.dataframe(pred_df)

    # Download
    st.download_button(
        label="Download CSV",
        data=pred_df.to_csv().encode(),
        file_name="forecast.csv",
        mime="text/csv",
    )

else:
    st.info("Click **Run Forecast** to generate predictions.")
