import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime, timedelta

# -------------------------------------------------------------------
# CONFIG
# -------------------------------------------------------------------
ML_SERVICE_URL = "http://158.180.57.220:5001"
PREDICT_ENDPOINT = f"{ML_SERVICE_URL}/predict-electricity"
HEALTH_ENDPOINT = f"{ML_SERVICE_URL}/health"

st.set_page_config(
    page_title="UK Electricity Demand Predictor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------
@st.cache_data(ttl=30)
def get_model_info():
    """Fetch model info from ML service."""
    try:
        r = requests.get(HEALTH_ENDPOINT, timeout=3)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {
            "electricity_model_loaded": False,
            "status": "degraded"
        }


def predict_single_hour(year, month, day, hour):
    """Call ML service API to predict for a single hour."""
    try:
        payload = {
            "year": year,
            "month": month,
            "day": day,
            "hour": hour
        }
        r = requests.post(PREDICT_ENDPOINT, json=payload, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Prediction failed: {e}")
        return None


def generate_forecast(start_datetime, hours):
    """Generate forecast by calling API for each hour."""
    results = []
    current_dt = start_datetime

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(hours):
        status_text.text(f"Generating forecast: {i+1}/{hours} hours...")
        progress_bar.progress((i + 1) / hours)

        result = predict_single_hour(
            year=current_dt.year,
            month=current_dt.month,
            day=current_dt.day,
            hour=current_dt.hour
        )

        if result and "demand_mw" in result:
            results.append({
                "timestamp": current_dt,
                "demand_mw": result["demand_mw"]
            })
        else:
            st.error(f"Failed to get prediction for {current_dt}")
            break

        current_dt += timedelta(hours=1)

    progress_bar.empty()
    status_text.empty()

    if results:
        return pd.DataFrame(results).set_index("timestamp")
    return None


# -------------------------------------------------------------------
# HEADER
# -------------------------------------------------------------------
st.title("⚡ UK Electricity Demand Predictor")
st.markdown("Forecast electricity demand using ML predictions from Oracle Cloud backend")

# Backend status
ml_info = get_model_info()
backend_status = ml_info.get("status", "unknown")
elec_loaded = ml_info.get("electricity_model_loaded", False)

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"""
    **Backend Status:** {'🟢 Healthy' if backend_status == 'healthy' else '🔴 Degraded'}
    **Electricity Model:** {'✅ Loaded' if elec_loaded else '❌ Not Loaded'}
    """)
with col2:
    if st.button("🔄 Refresh Status"):
        st.cache_data.clear()
        st.rerun()

if not elec_loaded:
    st.error("⚠️ Electricity model is not loaded on the backend. Please check the ML service.")
    st.stop()

st.markdown("---")

# -------------------------------------------------------------------
# SIDEBAR SETTINGS
# -------------------------------------------------------------------
st.sidebar.header("⚙️ Forecast Settings")

# Start date/time
st.sidebar.subheader("Start Date & Time")
start_date = st.sidebar.date_input(
    "Start Date",
    value=datetime.now().date(),
    min_value=datetime(2025, 1, 1).date(),
    max_value=datetime(2030, 12, 31).date()
)
start_hour = st.sidebar.slider("Start Hour", 0, 23, datetime.now().hour)

# Forecast horizon
st.sidebar.subheader("Forecast Horizon")
mode = st.sidebar.radio("Horizon Type", ["Hours", "Days", "Weeks"])

if mode == "Hours":
    horizon = st.sidebar.slider("Hours to forecast", 1, 72, 24)
elif mode == "Days":
    horizon = st.sidebar.slider("Days to forecast", 1, 7, 3) * 24
else:
    horizon = st.sidebar.slider("Weeks to forecast", 1, 4, 1) * 7 * 24

# Create start datetime
start_datetime = datetime.combine(start_date, datetime.min.time().replace(hour=start_hour))

st.sidebar.markdown("---")
st.sidebar.info(f"""
**Summary:**
- Start: {start_datetime.strftime('%Y-%m-%d %H:%00')}
- Forecast: {horizon} hours
- End: {(start_datetime + timedelta(hours=horizon-1)).strftime('%Y-%m-%d %H:%00')}
""")

# -------------------------------------------------------------------
# MAIN CONTENT
# -------------------------------------------------------------------
if st.button("🚀 Generate Forecast", use_container_width=True, type="primary"):

    with st.spinner("Generating forecast from backend..."):
        forecast_df = generate_forecast(start_datetime, horizon)

    if forecast_df is not None and not forecast_df.empty:
        st.success(f"✅ Generated {len(forecast_df)} hour forecast!")

        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📉 Min Demand", f"{forecast_df['demand_mw'].min():,.0f} MW")
        with col2:
            st.metric("📊 Avg Demand", f"{forecast_df['demand_mw'].mean():,.0f} MW")
        with col3:
            st.metric("📈 Max Demand", f"{forecast_df['demand_mw'].max():,.0f} MW")

        # Chart
        st.subheader("📊 Demand Forecast")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=forecast_df.index,
            y=forecast_df["demand_mw"],
            mode='lines+markers',
            name='Forecast',
            line=dict(color='#00D9FF', width=3),
            marker=dict(size=4)
        ))
        fig.update_layout(
            template="plotly_dark",
            height=500,
            xaxis_title="Date & Time",
            yaxis_title="Demand (MW)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

        # Data table
        with st.expander("📋 View Forecast Data"):
            display_df = forecast_df.copy()
            display_df.index = display_df.index.strftime('%Y-%m-%d %H:%00')
            display_df['demand_mw'] = display_df['demand_mw'].round(2)
            st.dataframe(display_df, use_container_width=True)

        # Download
        csv = forecast_df.to_csv()
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"electricity_forecast_{start_datetime.strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.error("❌ Failed to generate forecast. Please check backend connection.")
else:
    st.info("👆 Click the button above to generate an electricity demand forecast")

# -------------------------------------------------------------------
# FOOTER
# -------------------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Powered by PyCaret ML Model • Backend: Oracle Cloud • Frontend: Streamlit Cloud</p>
    <p>🤖 Generated with <a href='https://claude.com/claude-code'>Claude Code</a></p>
</div>
""", unsafe_allow_html=True)
