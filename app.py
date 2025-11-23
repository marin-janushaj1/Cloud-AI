import numpy as np
import pandas as pd
import streamlit as st
import joblib
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

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
# Load model bundle
# ------------------------------------------------------------
@st.cache_resource
def load_model():
    """Load the trained model with caching"""
    bundle_path = Path("data/clean/best_model.pkl")

    if not bundle_path.exists():
        st.error(f"Model not found at {bundle_path}. Please run notebook 4 to train the model.")
        st.stop()

    try:
        bundle = joblib.load(bundle_path)

        if isinstance(bundle, dict) and 'model' in bundle:
            return bundle
        else:
            st.error("Invalid model format. Please retrain using notebook 4.")
            st.stop()
    except Exception as e:
        st.error(f"Error loading model: {e}")
        st.stop()

bundle = load_model()
model = bundle['model']
target_encoder = bundle.get('target_encoder')
feature_names = bundle.get('feature_names')
metrics = bundle.get('metrics', {})
metadata = bundle.get('metadata', {})

# ------------------------------------------------------------
# Sidebar - Model Information
# ------------------------------------------------------------
with st.sidebar:
    st.header("📊 Model Information")

    st.markdown(f"""
    **Model Type:** {bundle.get('model_name', 'Unknown')}
    **Training Date:** {metadata.get('training_date', 'N/A')}
    **Training Samples:** {metadata.get('training_samples', 'N/A'):,}
    """)

    st.divider()

    st.subheader("Performance Metrics")
    st.metric("R² Score", f"{metrics.get('test_r2', 0):.3f}")
    st.metric("Mean Absolute Error", f"£{metrics.get('test_mae', 0):,.0f}")
    st.metric("RMSE", f"£{metrics.get('test_rmse', 0):,.0f}")

    st.divider()

    st.subheader("About")
    st.markdown("""
    This predictor uses historical UK housing data (1995-2017) to estimate property prices based on:
    - Property type
    - Location (county)
    - Age (new/established)
    - Tenure type
    - Year of sale
    """)

    st.divider()
    st.caption("Built with Streamlit & scikit-learn")

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
# Feature builder
# ------------------------------------------------------------
def make_features(property_type: str, is_new: str, duration: str,
                  county: str, year: int, month: int, quarter: int) -> pd.DataFrame:
    """Create feature DataFrame matching training format"""

    row = pd.DataFrame([{
        "type": property_type,
        "is_new": is_new,
        "duration": duration,
        "county": county.upper(),
        "year": year,
        "month": month,
        "quarter": quarter
    }])

    # Target encode county
    if target_encoder is not None:
        try:
            enc_df = target_encoder.transform(row[["county"]])
            row["county_encoded"] = enc_df["county"]
        except:
            row["county_encoded"] = 0.0
    else:
        row["county_encoded"] = 0.0

    row = row.drop(columns=["county"])

    # One-hot encode categorical features (don't drop first to get all columns)
    row = pd.get_dummies(row, columns=["type", "is_new", "duration"], drop_first=False)

    # Now drop the reference categories to match training (D, N, F are dropped during training)
    cols_to_drop = ['type_D', 'is_new_N', 'duration_F']
    row = row.drop(columns=[col for col in cols_to_drop if col in row.columns])

    # Align to training features
    if feature_names is not None:
        for col in feature_names:
            if col not in row.columns:
                row[col] = 0
        row = row[feature_names]

    return row

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

    # Calculate quarter from month automatically
    quarter = (month - 1) // 3 + 1

st.divider()

# Predict button
predict_button = st.button("🔮 Predict House Price", type="primary", use_container_width=True)

# ------------------------------------------------------------
# Prediction & Results
# ------------------------------------------------------------
if predict_button:
    with st.spinner("Analyzing property data..."):
        try:
            # Make prediction
            X_row = make_features(
                property_type=property_type,
                is_new=is_new,
                duration=duration,
                county=county,
                year=year,
                month=month,
                quarter=quarter
            )

            # Predict (model always returns log-transformed values)
            y_log = model.predict(X_row)[0]

            # Convert back from log scale (log1p inverse is expm1)
            # Model was trained with np.log1p(price), so we use np.expm1 to reverse
            predicted_price = float(np.expm1(y_log))

            # Sanity check: realistic UK house prices are between £50K and £5M
            if predicted_price < 1000 or predicted_price > 10_000_000:
                st.warning(f"⚠️ Unusual prediction detected: £{predicted_price:,.0f}. This might indicate a data issue.")
                st.info(f"Debug: Log prediction value was {y_log:.4f}")

            # Calculate confidence interval
            mae = metrics.get('test_mae', 50000)
            lower_bound = max(1000, predicted_price - 2 * mae)
            upper_bound = predicted_price + 2 * mae

            # Display results
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
                    label="Lower Estimate (95% CI)",
                    value=f"£{lower_bound:,.0f}",
                    delta=f"-{((predicted_price - lower_bound) / predicted_price * 100):.1f}%"
                )

            with col3:
                st.metric(
                    label="Upper Estimate (95% CI)",
                    value=f"£{upper_bound:,.0f}",
                    delta=f"+{((upper_bound - predicted_price) / predicted_price * 100):.1f}%"
                )

            # Visualization
            st.subheader("📈 Price Confidence Interval")

            fig = go.Figure()

            # Add confidence interval bar
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
                title="Price Estimate with 95% Confidence Interval",
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

            # Price per square foot estimate (rough)
            st.info(f"""
            💡 **Insight:** Based on historical data, this {property_type_name.lower()} in {county}
            is estimated at **£{predicted_price:,.0f}** with a confidence range of
            **£{lower_bound:,.0f} - £{upper_bound:,.0f}**.
            """)

            # Debug information (expandable)
            with st.expander("🔍 Technical Details"):
                st.write("**Model Input Features:**")
                st.dataframe(X_row, use_container_width=True)
                st.write(f"**Log-transformed prediction:** {y_log:.4f}")
                st.write(f"**Model:** {bundle.get('model_name', 'Unknown')}")
                st.write(f"**Number of features:** {len(feature_names) if feature_names else 'N/A'}")

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
    <p>Model trained on 22M+ transactions from 1995-2017</p>
    <p><em>For educational purposes only. Predictions should not be used for actual property valuation.</em></p>
</div>
""", unsafe_allow_html=True)
