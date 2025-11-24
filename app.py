import numpy as np
import pandas as pd
import streamlit as st
import requests
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

API_BASE_URL = "http://158.180.57.220:8080/api/v1"

# Page config
st.set_page_config(
    page_title="UK House Price Predictor",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🏡 UK House Price Predictor</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Team Yunus — Cloud AI | Powered by Machine Learning</p>', unsafe_allow_html=True)

# ------------------------------------------------------------
# Sidebar - Model Information (static for cloud deployment)
# ------------------------------------------------------------
with st.sidebar:
    st.header("📊 Model Information")

    st.markdown(f"""
    **Model Type:** LightGBM Regressor (remote API)
    **Deployment:** Oracle Cloud VM + Docker
    """)

    st.divider()

    st.subheader("Performance Metrics")
    st.metric("R² Score", "N/A")
    st.metric("Mean Absolute Error", "N/A")
    st.metric("RMSE", "N/A")

    st.divider()

    st.subheader("About")
    st.markdown("""
    This predictor uses historical UK housing data (1995-2017) via a cloud-hosted
    ML service. Your input is sent to a backend API, which runs a trained model
    and returns the predicted price and confidence interval.
    """)

    st.divider()
    st.caption("Backend: Python ML service + Go API Gateway on Oracle Cloud")

# ------------------------------------------------------------
# County mapping for user-friendly selection
# ------------------------------------------------------------
POPULAR_COUNTIES = [
    "GREATER LONDON",
    "GREATER MANCHESTER",
    "WEST MIDLANDS",
    "WEST YORKSHIRE",
    "KENT",
    "ESSEX",
    "SURREY",
    "HAMPSHIRE",
    "LANCASHIRE",
    "HERTFORDSHIRE",
    "BRISTOL",
    "CORNWALL",
    "DEVON",
    "OXFORDSHIRE",
    "CAMBRIDGESHIRE"
]

PROPERTY_TYPE_MAP = {
    "Detached": "D",
    "Semi-Detached": "S",
    "Terraced": "T",
    "Flat/Apartment": "F",
    "Other": "O"
}

# ------------------------------------------------------------
# Main Interface
# ------------------------------------------------------------
st.subheader("🏠 Enter Property Details")

# Create two columns for better layout
col1, col2 = st.columns(2)

with col1:
    property_type_name = st.selectbox(
        "Property Type",
        options=list(PROPERTY_TYPE_MAP.keys()),
        index=2,
        help="Select the type of property"
    )
    property_type = PROPERTY_TYPE_MAP[property_type_name]

    is_new_label = st.selectbox(
        "Property Age",
        options=["Established Build", "New Build"],
        index=0
    )
    is_new = "Y" if is_new_label == "New Build" else "N"

    duration_label = st.selectbox(
        "Tenure Type",
        options=["Freehold", "Leasehold"],
        index=0,
        help="Freehold: you own the property and land. Leasehold: you own for a fixed period"
    )
    duration = "F" if duration_label == "Freehold" else "L"

with col2:
    county = st.selectbox(
        "County/Region",
        options=POPULAR_COUNTIES,
        index=0,
        help="Select the county where the property is located"
    )

    year = st.slider(
        "Year of Transfer",
        min_value=1995,
        max_value=2017,
        value=2016,
        help="Year when the property was/will be sold"
    )

    # Month selection (quarter is automatically calculated)
    month = st.selectbox(
        "Month",
        options=list(range(1, 13)),
        format_func=lambda x: [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ][x-1],
        index=0,
        help="Month when the property was/will be sold"
    )

    # Calculate quarter from month automatically (for display)
    quarter = (month - 1) // 3 + 1

st.divider()

# Predict button
predict_button = st.button("🔮 Predict House Price", type="primary", use_container_width=True)

# ------------------------------------------------------------
# Prediction & Results (via backend API)
# ------------------------------------------------------------
if predict_button:
    with st.spinner("Sending data to cloud ML service..."):
        try:
            payload = {
                "property_type": property_type,
                "is_new": is_new,
                "duration": duration,
                "county": county,
                "year": year,
                "month": month
                # quarter is typically derived in backend if needed
            }

            response = requests.post(
                f"{API_BASE_URL}/predict/housing",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            # Expected keys from API:
            # price, confidence_lower, confidence_upper (if implemented)
            predicted_price = float(data.get("price", 0))
            lower_bound = data.get("confidence_lower")
            upper_bound = data.get("confidence_upper")

            # Fallback if API didn't send CI
            if lower_bound is None or upper_bound is None:
                # basic ±25% fallback
                lower_bound = max(1000, predicted_price * 0.75)
                upper_bound = predicted_price * 1.25

            # Sanity check: realistic UK house prices
            if predicted_price < 1000 or predicted_price > 10_000_000:
                st.warning(f"⚠️ Unusual prediction detected: £{predicted_price:,.0f}.")
            
            st.success("✅ Prediction Complete!")

            # Main price display
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    label="Predicted Price",
                    value=f"£{predicted_price:,.0f}",
                    delta=None
                )

            with col2:
                st.metric(
                    label="Lower Estimate",
                    value=f"£{lower_bound:,.0f}"
                )

            with col3:
                st.metric(
                    label="Upper Estimate",
                    value=f"£{upper_bound:,.0f}"
                )

            # Visualization
            st.subheader("📈 Price Confidence Interval")

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=['Estimated Price'],
                y=[predicted_price],
                error_y=dict(
                    type='data',
                    symmetric=False,
                    array=[upper_bound - predicted_price],
                    arrayminus=[predicted_price - lower_bound]
                ),
                marker_color='#1f77b4',
                name='Predicted Price'
            ))

            fig.update_layout(
                title="Price Estimate with Confidence Interval",
                yaxis_title="Price (£)",
                showlegend=False,
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

            # Property Summary
            st.subheader("📋 Property Summary")
            summary_col1, summary_col2 = st.columns(2)

            with summary_col1:
                st.markdown(f"""
                **Property Details:**
                - Type: {property_type_name}
                - Age: {is_new_label}
                - Tenure: {duration_label}
                """)

            with summary_col2:
                month_names = ["January", "February", "March", "April", "May", "June",
                              "July", "August", "September", "October", "November", "December"]
                st.markdown(f"""
                **Location & Time:**
                - County: {county}
                - Year: {year}
                - Month: {month_names[month-1]}
                """)

            st.info(f"""
            💡 **Insight:** Based on the cloud-hosted ML model, this {property_type_name.lower()} in {county}
            is estimated at **£{predicted_price:,.0f}** with a range of
            **£{lower_bound:,.0f} - £{upper_bound:,.0f}**.
            """)

            # Debug / API response
            with st.expander("🔍 Technical API Details"):
                st.write("**Raw API Response:**")
                st.json(data)

        except Exception as e:
            st.error(f"❌ Prediction failed: {e}")
            with st.expander("Show Error Details"):
                import traceback
                st.code(traceback.format_exc())

# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>🎓 <strong>UK Housing Price Prediction Project</strong> | Team Yunus</p>
    <p>Model served via Dockerized ML microservice + Go API gateway on Oracle Cloud.</p>
    <p><em>For educational purposes only. Predictions should not be used for actual property valuation.</em></p>
</div>
""", unsafe_allow_html=True)
