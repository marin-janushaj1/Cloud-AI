import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from pycaret.regression import load_model, predict_model

st.set_page_config(page_title="⚡ UK Electricity Demand Forecast", page_icon="⚡", layout="centered")

st.title("⚡ UK Electricity Demand Forecast Dashboard")
st.caption("Team Yunus — Cloud AI")

# ------------------------------------------------------------
# Load model and dataset
# ------------------------------------------------------------
MODEL_PATH = Path("data/clean/electricity_model.pkl")
DATA_PATH = Path("data/clean/uk_electricity_hourly.parquet")

if not MODEL_PATH.exists() or not DATA_PATH.exists():
    st.error("Model or data file missing. Please ensure both files exist in data/clean/")
    st.stop()

# Load trained model (PyCaret)
model = load_model(str(MODEL_PATH.with_suffix("")))  # PyCaret expects base name without .pkl
# Load dataset
df = pd.read_parquet(DATA_PATH)
df = df.reset_index().rename(columns={"index": "timestamp"})
df["timestamp"] = pd.to_datetime(df["timestamp"])

# ------------------------------------------------------------
# Sidebar controls
# ------------------------------------------------------------
st.sidebar.header("Forecast Settings")
n_hours = st.sidebar.slider("Forecast horizon (hours)", 1, 72, 24)
show_history = st.sidebar.slider("Show last N hours of history", 24, 168, 48)

# ------------------------------------------------------------
# Prepare features for forecast
# ------------------------------------------------------------
last_ts = df["timestamp"].max()
future_ts = pd.date_range(last_ts + pd.Timedelta(hours=1), periods=n_hours, freq="H")

future = pd.DataFrame({"timestamp": future_ts})
future["hour"] = future["timestamp"].dt.hour
future["day"] = future["timestamp"].dt.day
future["month"] = future["timestamp"].dt.month
future["weekday"] = future["timestamp"].dt.weekday
future["is_weekend"] = (future["weekday"] >= 5).astype(int)

# Make predictions
pred = predict_model(model, data=future.copy())

# Handle column naming difference
pred_col = "prediction_label" if "prediction_label" in pred.columns else "Label"
forecast = pred[["timestamp", pred_col]].rename(columns={pred_col: "forecast_mw"})

# ------------------------------------------------------------
# Visualization
# ------------------------------------------------------------
st.subheader(f"Forecast for next {n_hours} hours")

# Combine recent history + forecast
hist = df.tail(show_history)[["timestamp", "demand_mw"]]
plt.figure(figsize=(10, 4))
plt.plot(hist["timestamp"], hist["demand_mw"], label="History", color="tab:blue")
plt.plot(forecast["timestamp"], forecast["forecast_mw"], label="Forecast", color="tab:orange")
plt.xlabel("Time")
plt.ylabel("Demand (MW)")
plt.title("UK Electricity Demand — Recent History & Forecast")
plt.legend()
plt.grid(True)
st.pyplot(plt)

# ------------------------------------------------------------
# Summary statistics
# ------------------------------------------------------------
avg_future = forecast["forecast_mw"].mean()
peak_future = forecast["forecast_mw"].max()
low_future = forecast["forecast_mw"].min()

st.metric("Average Forecasted Demand (MW)", f"{avg_future:,.0f}")
st.metric("Peak Forecasted Demand (MW)", f"{peak_future:,.0f}")
st.metric("Lowest Forecasted Demand (MW)", f"{low_future:,.0f}")

# ------------------------------------------------------------
# Data preview
# ------------------------------------------------------------
with st.expander("🔍 Show forecast data"):
    st.dataframe(forecast, use_container_width=True)

st.success("✅ Forecast generated successfully!")